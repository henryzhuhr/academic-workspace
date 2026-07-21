#!/usr/bin/env python3
"""Manage projects and literature in the academic workspace."""

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unicodedata
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import unquote

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "workspace.json"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ARXIV_RE = re.compile(r"(?<![0-9])([0-9]{4}\.[0-9]{4,5})(v[0-9]+)?(?![0-9])", re.I)
BIB_KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9:_-]*$")
READING_STATUSES = ("queued", "reading", "extracting", "done", "dropped")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "for",
    "from",
    "in",
    "of",
    "on",
    "the",
    "to",
    "with",
}

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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_authors(value: str) -> List[str]:
    if ";" in value:
        parts = value.split(";")
    elif re.search(r"\s+and\s+", value, flags=re.I):
        parts = re.split(r"\s+and\s+", value, flags=re.I)
    else:
        parts = [value]
    return [part.strip() for part in parts if part.strip()]


def bibtex_author(author: str) -> str:
    if "," in author:
        return author.strip()
    parts = author.split()
    if len(parts) < 2:
        return author.strip()
    return "{}, {}".format(parts[-1], " ".join(parts[:-1]))


def family_name(author: str) -> str:
    if "," in author:
        return author.split(",", 1)[0].strip()
    parts = author.split()
    return parts[-1] if parts else "unknown"


def ascii_words(value: str) -> List[str]:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.findall(r"[a-z0-9]+", ascii_value.casefold())


def short_title_words(title: str) -> List[str]:
    words = [word for word in ascii_words(title) if word not in STOP_WORDS]
    return words[:4] or ["paper"]


def bibtex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "%": r"\%",
        "&": r"\&",
        "_": r"\_",
        "#": r"\#",
    }
    return "".join(replacements.get(character, character) for character in value)


def pdf_record(path: Path) -> Tuple[str, List[str], Optional[int], int]:
    try:
        with path.open("rb") as handle:
            if handle.read(5) != b"%PDF-":
                raise WorkspaceError("文件不是有效 PDF：{}".format(path))
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            raise WorkspaceError("暂不支持加密 PDF：{}".format(path))
        metadata = reader.metadata
        title = (metadata.title or "").strip() if metadata else ""
        authors = split_authors((metadata.author or "").strip()) if metadata else []
        year: Optional[int] = None
        if metadata:
            raw_date = str(metadata.get("/CreationDate", ""))
            match = re.search(r"(?:D:)?((?:19|20)[0-9]{2})", raw_date)
            if match:
                year = int(match.group(1))
        return title, authors, year, len(reader.pages)
    except WorkspaceError:
        raise
    except Exception as exc:
        raise WorkspaceError("无法读取 PDF：{} ({})".format(path, exc)) from exc


def parse_arxiv(value: str) -> Tuple[str, str]:
    match = ARXIV_RE.search(value)
    if not match:
        raise WorkspaceError("arXiv 编号无效：{}".format(value))
    return match.group(1), (match.group(2) or "").lower()


def infer_year(arxiv_id: str) -> int:
    return 2000 + int(arxiv_id[:2])


def render_bibtex_entry(
    key: str,
    title: str,
    authors: Sequence[str],
    year: int,
    local_file: str,
    checksum: str,
    arxiv_id: str,
    arxiv_version: str,
    doi: str,
    url: str,
) -> str:
    fields = [
        ("title", title),
        ("author", " and ".join(bibtex_author(author) for author in authors)),
        ("year", str(year)),
    ]
    if arxiv_id:
        fields.extend((("eprint", arxiv_id), ("archivePrefix", "arXiv")))
    if doi:
        fields.append(("doi", doi))
    if url:
        fields.append(("url", url))
    lines = [
        "% local_file: {}".format(local_file),
        "% sha256: {}".format(checksum),
        "@misc{{{},".format(key),
    ]
    lines.extend(
        "  {} = {{{}}},".format(name, bibtex_escape(value)) for name, value in fields
    )
    if arxiv_version:
        lines.append("  note = {{arXiv:{}{}}},".format(arxiv_id, arxiv_version))
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_reading_note(
    key: str,
    title: str,
    authors: Sequence[str],
    year: int,
    venue: str,
    url: str,
    local_file: str,
    checksum: str,
    pages: int,
    status: str,
    projects: Sequence[str],
    today: str,
) -> str:
    project_text = ", ".join("`{}`".format(project) for project in projects) or "_TBD_"
    return """# {key} — {title}

## Bibliographic record

| Field | Value |
| --- | --- |
| BibTeX key | `{key}` |
| Authors | {authors} |
| Year | {year} |
| Venue | {venue} |
| DOI / URL | {url} |
| Local file | `{local_file}` |
| SHA-256 | `{checksum}` |
| PDF pages | {pages} |
| Reading status | `{status}` |
| Updated | {today} |

## One-sentence contribution

_TBD — 尚未核对正文，不得根据标题推断贡献。_

## Research question and context

_TBD_

## Claims and evidence

| Claim | Evidence or method | Location | Confidence / limitation |
| --- | --- | --- | --- |
| _TBD_ | _TBD_ | _TBD_ | _TBD_ |

## Methods

_TBD_

## Limitations and contradictions

_TBD_

## Reusable insights

- _TBD_

## Related projects and topics

- Project IDs: {projects}
- Topic reviews: _TBD_

## Follow-up

- 核对书目信息、核心主张、方法、限制和对应页码。
""".format(
        key=key,
        title=title,
        authors="; ".join(authors),
        year=year,
        venue=venue or "_TBD_",
        url=url or "_TBD_",
        local_file=local_file,
        checksum=checksum,
        pages=pages,
        status=status,
        today=today,
        projects=project_text,
    )


def append_reading_queue(
    content: str,
    title: str,
    note_name: str,
    status: str,
    priority: str,
    projects: Sequence[str],
    next_action: str,
    today: str,
) -> str:
    link = "[{}](../literature/reading-notes/{})".format(title, note_name)
    project_text = ", ".join("`{}`".format(project) for project in projects) or "—"
    row = "| {} | `{}` | {} | {} | {} | {} |".format(
        markdown_cell(link),
        status,
        priority,
        project_text,
        markdown_cell(next_action),
        today,
    )
    if link in content:
        raise WorkspaceError("阅读队列已包含该文献：{}".format(title))
    lines = content.rstrip().splitlines()
    try:
        header_index = next(
            index for index, line in enumerate(lines) if line.startswith("| Item |")
        )
    except StopIteration as exc:
        raise WorkspaceError("dashboard/reading.md 缺少阅读队列表格") from exc
    insert_at = header_index + 2
    while insert_at < len(lines) and lines[insert_at].startswith("|"):
        insert_at += 1
    lines.insert(insert_at, row)
    return "\n".join(lines) + "\n"


def find_pdf_by_hash(files_root: Path, checksum: str) -> Optional[Path]:
    for candidate in files_root.rglob("*.pdf"):
        if candidate.is_file() and sha256_file(candidate) == checksum:
            return candidate
    return None


def atomic_copy_pdf(source: Path, target: Path, checksum: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=".{}-".format(target.name), suffix=".tmp", dir=str(target.parent)
    )
    os.close(descriptor)
    try:
        shutil.copy2(str(source), temp_name)
        if sha256_file(Path(temp_name)) != checksum:
            raise WorkspaceError("复制后的 PDF 校验失败")
        os.replace(temp_name, str(target))
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


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


def command_paper_add(config: Dict[str, Any], args: argparse.Namespace) -> int:
    source = Path(args.source).expanduser().resolve()
    if not source.is_file():
        raise WorkspaceError("PDF 不存在：{}".format(source))
    if source.suffix.casefold() != ".pdf":
        raise WorkspaceError("仅支持 PDF 文件：{}".format(source))

    files_link = workspace_path(config["literatureFiles"])
    if not files_link.is_symlink() or not files_link.exists():
        raise WorkspaceError(
            "{} 必须是指向仓库外文献库的有效软链接".format(
                config["literatureFiles"]
            )
        )
    files_root = files_link.resolve()
    try:
        files_root.relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        raise WorkspaceError("文献全文库必须位于 Git 仓库之外")

    title_from_pdf, authors_from_pdf, year_from_pdf, pages = pdf_record(source)
    title = (args.title or title_from_pdf).strip()
    authors = args.author or authors_from_pdf
    if not title:
        raise WorkspaceError("PDF 缺少标题元数据；请使用 --title 补充")
    if not authors:
        raise WorkspaceError("PDF 缺少作者元数据；请使用 --author 补充")
    if any(not author.strip() for author in authors):
        raise WorkspaceError("作者不得为空")

    arxiv_source = args.arxiv or source.name
    arxiv_id = ""
    arxiv_version = ""
    if args.arxiv or ARXIV_RE.search(source.name):
        arxiv_id, arxiv_version = parse_arxiv(arxiv_source)
    year = args.year or (infer_year(arxiv_id) if arxiv_id else year_from_pdf)
    if year is None or year < 1900 or year > dt.date.today().year + 1:
        raise WorkspaceError("无法可靠确定年份；请使用 --year 补充")

    projects = list(dict.fromkeys(args.project))
    for project in projects:
        if not SLUG_RE.fullmatch(project):
            raise WorkspaceError("项目 id 无效：{}".format(project))
        project_dir = workspace_path(config["projectsRoot"]) / project
        if not (project_dir / config["projectMetadataFile"]).is_file():
            raise WorkspaceError("项目不存在：{}".format(project))

    author_slug_parts = ascii_words(family_name(authors[0]))
    author_slug = "-".join(author_slug_parts) or "unknown"
    title_words = short_title_words(title)
    title_slug = "-".join(title_words)
    citation_key = args.citation_key or "{}{}{}".format(
        "".join(author_slug_parts) or "paper",
        year,
        title_words[0] + "".join(word.capitalize() for word in title_words[1:]),
    )
    if not BIB_KEY_RE.fullmatch(citation_key):
        raise WorkspaceError("BibTeX key 无效：{}".format(citation_key))

    source_version = arxiv_id + arxiv_version
    identifier_suffix = "-{}".format(source_version) if source_version else ""
    venue_slug = "arxiv" if arxiv_id else "paper"
    filename = "{}-{}-{}-{}{}.pdf".format(
        year, venue_slug, author_slug, title_slug, identifier_suffix
    )
    note_name = "{}-{}-{}-{}.md".format(
        year, venue_slug, author_slug, title_slug
    )
    checksum = sha256_file(source)

    duplicate = find_pdf_by_hash(files_root, checksum)
    target = duplicate or files_root / "papers" / str(year) / filename
    if target.exists() and sha256_file(target) != checksum:
        raise WorkspaceError("目标文件已存在但内容不同：{}".format(target))
    relative_external = target.resolve().relative_to(files_root)
    local_file = str(Path(config["literatureFiles"]) / relative_external)

    bibliography = workspace_path(config["bibliography"])
    bibliography_before = bibliography.read_text(encoding="utf-8")
    key_pattern = re.compile(r"@[A-Za-z]+\s*\{\s*" + re.escape(citation_key) + r"\s*,")
    if key_pattern.search(bibliography_before):
        raise WorkspaceError("BibTeX key 已存在：{}".format(citation_key))
    if arxiv_id and re.search(
        r"eprint\s*=\s*\{\s*" + re.escape(arxiv_id) + r"\s*\}",
        bibliography_before,
        flags=re.I,
    ):
        raise WorkspaceError("arXiv 文献已登记：{}".format(arxiv_id))

    url = args.url or (
        "https://arxiv.org/abs/{}{}".format(arxiv_id, arxiv_version)
        if arxiv_id
        else ""
    )
    venue = args.venue or ("arXiv preprint" if arxiv_id else "")
    bibtex_entry = render_bibtex_entry(
        citation_key,
        title,
        authors,
        year,
        local_file,
        checksum,
        arxiv_id,
        arxiv_version,
        args.doi,
        url,
    )
    bibliography_after = bibliography_before.rstrip() + "\n\n" + bibtex_entry

    note_path = ROOT / "literature" / "reading-notes" / note_name
    if note_path.exists():
        raise WorkspaceError("阅读笔记已存在：{}".format(note_path.relative_to(ROOT)))
    today = dt.date.today().isoformat()
    note_content = render_reading_note(
        citation_key,
        title,
        authors,
        year,
        venue,
        args.doi or url,
        local_file,
        checksum,
        pages,
        args.status,
        projects,
        today,
    )

    queue_path = ROOT / "dashboard" / "reading.md"
    queue_before = queue_path.read_text(encoding="utf-8")
    queue_after = queue_before
    if not args.no_queue:
        queue_after = append_reading_queue(
            queue_before,
            title,
            note_name,
            args.status,
            args.priority,
            projects,
            args.next_action,
            today,
        )

    print("论文：{}".format(title))
    print("作者：{}".format("; ".join(authors)))
    print("目标：{}".format(local_file))
    print("BibTeX：{}".format(citation_key))
    print("阅读笔记：{}".format(note_path.relative_to(ROOT)))
    print("SHA-256：{}".format(checksum))
    if args.dry_run:
        print("预演完成：未写入任何文件")
        return 0

    copy_created = False
    bib_written = False
    note_written = False
    queue_written = False
    target_parent_existed = target.parent.exists()
    try:
        if duplicate is None and source != target.resolve():
            atomic_copy_pdf(source, target, checksum)
            copy_created = True
        atomic_write_text(bibliography, bibliography_after)
        bib_written = True
        atomic_write_text(note_path, note_content)
        note_written = True
        if not args.no_queue:
            atomic_write_text(queue_path, queue_after)
            queue_written = True
    except Exception:
        if queue_written:
            atomic_write_text(queue_path, queue_before)
        if note_written and note_path.exists():
            note_path.unlink()
        if bib_written:
            atomic_write_text(bibliography, bibliography_before)
        if copy_created and target.exists():
            target.unlink()
        if not target_parent_existed:
            try:
                target.parent.rmdir()
            except OSError:
                pass
        raise

    if duplicate is not None:
        print("全文已存在，复用：{}".format(local_file))
    else:
        print("已复制全文；原始下载文件保留不变")
    print("入库完成")
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

    paper_parser = subparsers.add_parser("paper", help="manage literature records")
    paper_subparsers = paper_parser.add_subparsers(dest="paper_command", required=True)
    paper_add_parser = paper_subparsers.add_parser(
        "add", help="archive a PDF and create traceable literature records"
    )
    paper_add_parser.add_argument("source")
    paper_add_parser.add_argument("--title")
    paper_add_parser.add_argument("--author", action="append", default=[])
    paper_add_parser.add_argument("--year", type=int)
    paper_add_parser.add_argument("--arxiv")
    paper_add_parser.add_argument("--doi", default="")
    paper_add_parser.add_argument("--url", default="")
    paper_add_parser.add_argument("--venue", default="")
    paper_add_parser.add_argument("--citation-key")
    paper_add_parser.add_argument("--project", action="append", default=[])
    paper_add_parser.add_argument(
        "--status", choices=READING_STATUSES, default="queued"
    )
    paper_add_parser.add_argument(
        "--priority", choices=("high", "medium", "low"), default="medium"
    )
    paper_add_parser.add_argument(
        "--next-action", default="核对核心贡献、方法、限制和对应页码"
    )
    paper_add_parser.add_argument("--no-queue", action="store_true")
    paper_add_parser.add_argument("--dry-run", action="store_true")
    paper_add_parser.set_defaults(handler=command_paper_add)
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
