#!/usr/bin/env python3
"""Manage the academic workspace without third-party dependencies."""

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "workspace.json"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

WORKSPACE_KEYS = {
    "$schema",
    "schemaVersion",
    "name",
    "projectsRoot",
    "projectTemplate",
    "projectMetadataFile",
    "projectsDashboard",
    "literatureFiles",
    "bibliography",
    "projectStatuses",
    "dataClassifications",
}

REQUIRED_ROOT_PATHS = (
    "README.md",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "pyproject.toml",
    "uv.lock",
    "package.json",
    "package-lock.json",
    "workspace.json",
    "inbox/README.md",
    "dashboard/README.md",
    "dashboard/projects.md",
    "dashboard/reading.md",
    "projects/README.md",
    "literature/README.md",
    "literature/bibliography.bib",
    "methods/README.md",
    "methods/data-management.md",
    "methods/reproducibility.md",
    "assets/README.md",
    "reports/README.md",
    "archive/README.md",
    "schemas/workspace.schema.json",
    "schemas/project.schema.json",
    "scripts/README.md",
)

REQUIRED_PROJECT_PATHS = (
    "project.json",
    "README.md",
    ".gitignore",
    "planning/README.md",
    "planning/decision-log.md",
    "notes/README.md",
    "data/README.md",
    "data/raw/README.md",
    "data/processed/README.md",
    "data/metadata/README.md",
    "analysis/README.md",
    "analysis/runs/README.md",
    "writing/README.md",
    "outputs/README.md",
    "archive/README.md",
)

PROJECT_KEYS = {
    "$schema",
    "schemaVersion",
    "id",
    "title",
    "status",
    "area",
    "summary",
    "owner",
    "started",
    "updated",
    "nextReview",
    "nextAction",
    "relatedProjects",
    "tags",
    "dataClassification",
}


class WorkspaceError(Exception):
    """A user-correctable workspace error."""


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise WorkspaceError("缺少文件：{}".format(path.relative_to(ROOT))) from exc
    except json.JSONDecodeError as exc:
        raise WorkspaceError(
            "JSON 无效：{}:{}:{} {}".format(
                path.relative_to(ROOT), exc.lineno, exc.colno, exc.msg
            )
        ) from exc
    if not isinstance(value, dict):
        raise WorkspaceError("JSON 根节点必须是对象：{}".format(path.relative_to(ROOT)))
    return value


def workspace_path(relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise WorkspaceError("workspace.json 包含不安全路径：{}".format(relative))
    return ROOT / path


def load_config() -> Dict[str, Any]:
    config = load_json(CONFIG_FILE)
    missing = sorted(WORKSPACE_KEYS - set(config))
    extra = sorted(set(config) - WORKSPACE_KEYS)
    if missing:
        raise WorkspaceError("workspace.json 缺少字段：{}".format(", ".join(missing)))
    if extra:
        raise WorkspaceError("workspace.json 包含未知字段：{}".format(", ".join(extra)))
    if config["schemaVersion"] != 2:
        raise WorkspaceError("不支持的 workspace schemaVersion")
    if not isinstance(config["name"], str) or not config["name"].strip():
        raise WorkspaceError("workspace.json.name 必须是非空字符串")
    for key in (
        "projectsRoot",
        "projectTemplate",
        "projectMetadataFile",
        "projectsDashboard",
        "literatureFiles",
        "bibliography",
    ):
        if not isinstance(config[key], str) or not config[key]:
            raise WorkspaceError("workspace.json.{} 必须是非空字符串".format(key))
        workspace_path(config[key])
    for key in ("projectStatuses", "dataClassifications"):
        values = config[key]
        if not isinstance(values, list) or not values or not all(
            isinstance(item, str) and item for item in values
        ):
            raise WorkspaceError("workspace.json.{} 必须是非空字符串数组".format(key))
        if len(values) != len(set(values)):
            raise WorkspaceError("workspace.json.{} 包含重复值".format(key))
    return config


def project_dirs(config: Dict[str, Any]) -> List[Path]:
    root = workspace_path(config["projectsRoot"])
    if not root.is_dir():
        raise WorkspaceError("项目根目录不存在：{}".format(root.relative_to(ROOT)))
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith("_")
    )


def valid_date(value: Any) -> bool:
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        return False
    try:
        dt.datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def validate_project(
    directory: Path, metadata: Dict[str, Any], config: Dict[str, Any]
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    prefix = "projects/{}".format(directory.name)

    missing_keys = sorted(PROJECT_KEYS - set(metadata))
    extra_keys = sorted(set(metadata) - PROJECT_KEYS)
    if missing_keys:
        errors.append("{}: project.json 缺少字段 {}".format(prefix, ", ".join(missing_keys)))
    if extra_keys:
        errors.append("{}: project.json 包含未知字段 {}".format(prefix, ", ".join(extra_keys)))

    if metadata.get("schemaVersion") != 1:
        errors.append("{}: schemaVersion 必须为 1".format(prefix))
    if not isinstance(metadata.get("$schema"), str) or not metadata["$schema"]:
        errors.append("{}: $schema 必须是非空字符串".format(prefix))

    project_id = metadata.get("id")
    if not isinstance(project_id, str) or not SLUG_RE.fullmatch(project_id):
        errors.append("{}: id 必须使用 lower-kebab-case".format(prefix))
    elif project_id != directory.name:
        errors.append("{}: id 必须与目录名一致".format(prefix))

    for key in ("title", "area"):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            errors.append("{}: {} 必须是非空字符串".format(prefix, key))
    for key in ("summary", "owner", "nextAction"):
        if not isinstance(metadata.get(key), str):
            errors.append("{}: {} 必须是字符串".format(prefix, key))

    if metadata.get("status") not in config["projectStatuses"]:
        errors.append("{}: status 不在允许列表中".format(prefix))
    if metadata.get("dataClassification") not in config["dataClassifications"]:
        errors.append("{}: dataClassification 不在允许列表中".format(prefix))

    for key in ("started", "updated"):
        if not valid_date(metadata.get(key)):
            errors.append("{}: {} 必须是有效 YYYY-MM-DD 日期".format(prefix, key))
    next_review = metadata.get("nextReview")
    if next_review != "" and not valid_date(next_review):
        errors.append("{}: nextReview 必须为空或有效 YYYY-MM-DD 日期".format(prefix))

    for key in ("relatedProjects", "tags"):
        value = metadata.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            errors.append("{}: {} 必须是字符串数组".format(prefix, key))
        elif len(value) != len(set(value)):
            errors.append("{}: {} 不得包含重复值".format(prefix, key))

    for related in metadata.get("relatedProjects", []) if isinstance(metadata.get("relatedProjects"), list) else []:
        if not isinstance(related, str):
            continue
        if not SLUG_RE.fullmatch(related):
            errors.append("{}: relatedProjects 包含无效 id {}".format(prefix, related))
        elif related == project_id:
            errors.append("{}: relatedProjects 不得引用项目自身".format(prefix))
    tags = metadata.get("tags")
    if isinstance(tags, list):
        for tag in tags:
            if isinstance(tag, str) and not tag.strip():
                errors.append("{}: tags 不得包含空字符串".format(prefix))

    status = metadata.get("status")
    if status in ("active", "writing"):
        if not metadata.get("nextAction", "").strip():
            errors.append("{}: {} 项目必须填写 nextAction".format(prefix, status))
        if not next_review:
            errors.append("{}: {} 项目必须填写 nextReview".format(prefix, status))

    if valid_date(next_review):
        review_date = dt.datetime.strptime(next_review, "%Y-%m-%d").date()
        if status in ("active", "writing") and review_date < dt.date.today():
            warnings.append("{}: nextReview 已过期 ({})".format(prefix, next_review))

    if valid_date(metadata.get("updated")):
        updated = dt.datetime.strptime(metadata["updated"], "%Y-%m-%d").date()
        if updated > dt.date.today():
            warnings.append("{}: updated 位于未来 ({})".format(prefix, metadata["updated"]))

    for relative in REQUIRED_PROJECT_PATHS:
        if not (directory / relative).exists():
            errors.append("{}: 缺少 {}".format(prefix, relative))

    readme = directory / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        if "{{" in text or "}}" in text:
            errors.append("{}: README.md 仍包含模板占位符".format(prefix))
    return errors, warnings


def load_project_records(
    config: Dict[str, Any]
) -> Tuple[List[Tuple[Path, Dict[str, Any]]], List[str], List[str]]:
    records: List[Tuple[Path, Dict[str, Any]]] = []
    errors: List[str] = []
    warnings: List[str] = []
    metadata_name = config["projectMetadataFile"]

    for directory in project_dirs(config):
        if directory.is_symlink():
            errors.append("projects/{}: 项目目录不得是软链接".format(directory.name))
            continue
        try:
            metadata = load_json(directory / metadata_name)
        except WorkspaceError as exc:
            errors.append(str(exc))
            continue
        project_errors, project_warnings = validate_project(directory, metadata, config)
        errors.extend(project_errors)
        warnings.extend(project_warnings)
        records.append((directory, metadata))

    known_ids = {
        metadata.get("id")
        for _, metadata in records
        if isinstance(metadata.get("id"), str)
    }
    for directory, metadata in records:
        for related in metadata.get("relatedProjects", []):
            if related not in known_ids:
                errors.append(
                    "projects/{}: relatedProjects 引用了不存在的项目 {}".format(
                        directory.name, related
                    )
                )
    return records, errors, warnings


def markdown_cell(value: Any) -> str:
    text = str(value) if value not in (None, "") else "—"
    return text.replace("|", "\\|").replace("\n", " ").strip()


def check_local_markdown_links() -> List[str]:
    errors: List[str] = []
    ignored_roots = {".git", ".agents", ".claude", "tmp"}
    for markdown in ROOT.rglob("*.md"):
        relative = markdown.relative_to(ROOT)
        if relative.parts and relative.parts[0] in ignored_roots:
            continue
        for line_number, line in enumerate(
            markdown.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for match in MARKDOWN_LINK_RE.finditer(line):
                target = match.group(1).strip().strip("<>")
                if (
                    not target
                    or target.startswith("#")
                    or "://" in target
                    or target.startswith(("mailto:", "doi:"))
                ):
                    continue
                target = unquote(target.split("#", 1)[0])
                resolved = (markdown.parent / target).resolve()
                if not resolved.exists():
                    errors.append(
                        "{}:{}: 本地链接不存在 {}".format(
                            relative, line_number, match.group(1)
                        )
                    )
    return errors


def render_dashboard(
    records: Sequence[Tuple[Path, Dict[str, Any]]], config: Dict[str, Any]
) -> str:
    status_order = {value: index for index, value in enumerate(config["projectStatuses"])}
    ordered = sorted(
        records,
        key=lambda item: (
            status_order.get(item[1].get("status"), 999),
            item[1].get("title", "").casefold(),
        ),
    )

    lines = [
        "# Projects",
        "",
        "> Generated from `projects/*/project.json` by `uv run scripts/workspace.py dashboard`. Do not edit project rows manually.",
        "",
    ]
    if not ordered:
        lines.append("_No research projects have been created yet._")
        lines.append("")
        return "\n".join(lines)

    counts: Dict[str, int] = {}
    for _, metadata in ordered:
        status = metadata["status"]
        counts[status] = counts.get(status, 0) + 1
    summary = ", ".join(
        "{} {}".format(status, counts[status])
        for status in config["projectStatuses"]
        if counts.get(status)
    )
    lines.extend(
        [
            "Portfolio: {} project(s) — {}.".format(len(ordered), summary),
            "",
            "| Project | Status | Area | Owner | Focus | Next action | Next review | Updated |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for directory, metadata in ordered:
        link = "[{}](../projects/{}/README.md)".format(metadata["title"], directory.name)
        row = (
            link,
            metadata["status"],
            metadata["area"],
            metadata["owner"],
            metadata["summary"],
            metadata["nextAction"],
            metadata["nextReview"],
            metadata["updated"],
        )
        lines.append("| {} |".format(" | ".join(markdown_cell(value) for value in row)))
    lines.append("")
    return "\n".join(lines)


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=".{}-".format(path.name), dir=str(path.parent), text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temp_name, str(path))
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def write_json(path: Path, value: Dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def update_dashboard(config: Dict[str, Any]) -> None:
    records, errors, _ = load_project_records(config)
    if errors:
        raise WorkspaceError("项目校验失败，未生成 dashboard：\n- " + "\n- ".join(errors))
    path = workspace_path(config["projectsDashboard"])
    atomic_write_text(path, render_dashboard(records, config))


def command_dashboard(config: Dict[str, Any], _args: argparse.Namespace) -> int:
    update_dashboard(config)
    print("已更新 {}".format(config["projectsDashboard"]))
    return 0


def command_new(config: Dict[str, Any], args: argparse.Namespace) -> int:
    slug = args.slug
    if not SLUG_RE.fullmatch(slug):
        raise WorkspaceError("项目 slug 必须使用 lower-kebab-case")

    projects_root = workspace_path(config["projectsRoot"])
    template = workspace_path(config["projectTemplate"])
    target = projects_root / slug
    if target.exists():
        raise WorkspaceError("项目已存在：projects/{}".format(slug))
    if not template.is_dir():
        raise WorkspaceError("项目模板不存在：{}".format(config["projectTemplate"]))

    today = dt.date.today()
    next_review = today + dt.timedelta(days=args.next_review_days)
    title = args.title or " ".join(part.capitalize() for part in slug.split("-"))
    tags = list(dict.fromkeys(args.tag))
    if not title.strip():
        raise WorkspaceError("项目 title 不得为空")
    if not args.area.strip():
        raise WorkspaceError("项目 area 不得为空")
    if any(not tag.strip() for tag in tags):
        raise WorkspaceError("项目 tag 不得为空")
    if args.status in ("active", "writing") and not args.next_action.strip():
        raise WorkspaceError("active 或 writing 项目必须填写 nextAction")

    temp = Path(tempfile.mkdtemp(prefix=".new-project-", dir=str(projects_root)))
    project_committed = False
    try:
        shutil.copytree(str(template), str(temp), dirs_exist_ok=True, symlinks=True)
        metadata_path = temp / config["projectMetadataFile"]
        metadata = load_json(metadata_path)
        metadata.update(
            {
                "id": slug,
                "title": title,
                "status": args.status,
                "area": args.area,
                "summary": args.summary,
                "owner": args.owner,
                "started": today.isoformat(),
                "updated": today.isoformat(),
                "nextReview": next_review.isoformat(),
                "nextAction": args.next_action,
                "tags": tags,
                "dataClassification": args.data_classification,
            }
        )
        write_json(metadata_path, metadata)

        replacements = {
            "{{project-id}}": slug,
            "{{project-title}}": title,
            "{{date}}": today.isoformat(),
        }
        for markdown in temp.rglob("*.md"):
            content = markdown.read_text(encoding="utf-8")
            for token, replacement in replacements.items():
                content = content.replace(token, replacement)
            atomic_write_text(markdown, content)

        os.replace(str(temp), str(target))
        project_committed = True
        update_dashboard(config)
    except Exception:
        if project_committed and target.exists() and not temp.exists():
            os.replace(str(target), str(temp))
        if temp.exists():
            shutil.rmtree(str(temp))
        raise

    print("已创建 projects/{}".format(slug))
    print("下一步：填写 projects/{}/README.md 并完善 project.json".format(slug))
    return 0


def command_check(config: Dict[str, Any], _args: argparse.Namespace) -> int:
    errors: List[str] = []
    warnings: List[str] = []

    for relative in REQUIRED_ROOT_PATHS:
        if not (ROOT / relative).exists():
            errors.append("缺少 {}".format(relative))

    for relative in ("schemas/workspace.schema.json", "schemas/project.schema.json"):
        try:
            load_json(ROOT / relative)
        except WorkspaceError as exc:
            errors.append(str(exc))

    template = workspace_path(config["projectTemplate"])
    if not template.is_dir():
        errors.append("缺少项目模板 {}".format(config["projectTemplate"]))
    else:
        for relative in REQUIRED_PROJECT_PATHS:
            if not (template / relative).exists():
                errors.append("项目模板缺少 {}".format(relative))

    literature_files = workspace_path(config["literatureFiles"])
    if not literature_files.is_symlink():
        warnings.append(
            "{} 缺失或不是软链接；文献文件任务开始前必须配置".format(
                config["literatureFiles"]
            )
        )
    elif not literature_files.exists():
        warnings.append("{} 是失效软链接".format(config["literatureFiles"]))

    records, project_errors, project_warnings = load_project_records(config)
    errors.extend(project_errors)
    warnings.extend(project_warnings)
    errors.extend(check_local_markdown_links())

    if not project_errors:
        expected_dashboard = render_dashboard(records, config)
        dashboard_path = workspace_path(config["projectsDashboard"])
        if dashboard_path.exists():
            actual_dashboard = dashboard_path.read_text(encoding="utf-8")
            if actual_dashboard != expected_dashboard:
                errors.append(
                    "{} 与项目元数据不同步；运行 dashboard 命令".format(
                        config["projectsDashboard"]
                    )
                )

    for warning in warnings:
        print("WARN  {}".format(warning))
    for error in errors:
        print("ERROR {}".format(error))

    if errors:
        print("检查失败：{} 个错误，{} 个警告".format(len(errors), len(warnings)))
        return 1
    print("检查通过：{} 个项目，{} 个警告".format(len(records), len(warnings)))
    return 0


def build_parser(config: Dict[str, Any]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Academic workspace manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="create a project from the template")
    new_parser.add_argument("slug")
    new_parser.add_argument("--title")
    new_parser.add_argument("--area", default="unclassified")
    new_parser.add_argument("--owner", default="")
    new_parser.add_argument("--summary", default="")
    new_parser.add_argument(
        "--next-action", default="Define the research question and scope."
    )
    new_parser.add_argument("--next-review-days", type=review_days, default=7, metavar="DAYS")
    new_parser.add_argument(
        "--status", choices=config["projectStatuses"], default="idea"
    )
    new_parser.add_argument(
        "--data-classification",
        choices=config["dataClassifications"],
        default="internal",
    )
    new_parser.add_argument("--tag", action="append", default=[])
    new_parser.set_defaults(handler=command_new)

    check_parser = subparsers.add_parser("check", help="validate the workspace")
    check_parser.set_defaults(handler=command_check)

    dashboard_parser = subparsers.add_parser(
        "dashboard", help="regenerate the projects dashboard"
    )
    dashboard_parser.set_defaults(handler=command_dashboard)
    return parser


def review_days(value: str) -> int:
    try:
        days = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("DAYS 必须是整数") from exc
    if not 1 <= days <= 365:
        raise argparse.ArgumentTypeError("DAYS 必须在 1 到 365 之间")
    return days


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        config = load_config()
        parser = build_parser(config)
        args = parser.parse_args(argv)
        return args.handler(config, args)
    except WorkspaceError as exc:
        print("ERROR {}".format(exc), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("已取消", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
