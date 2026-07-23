import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from pypdf import PdfWriter

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from jsonc import loads as jsonc_loads


SOURCE_ROOT = Path(__file__).resolve().parent.parent


class WorkspaceCliTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "workspace"
        self.external_library = Path(self.temporary_directory.name) / "literature-files"
        self.external_library.mkdir()
        shutil.copytree(
            SOURCE_ROOT,
            self.root,
            symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git",
                ".agents",
                ".claude",
                ".DS_Store",
                "tmp",
                "files",
                "__pycache__",
            ),
        )
        (self.root / "literature" / "files").symlink_to(
            self.external_library, target_is_directory=True
        )
        projects_root = self.root / "projects"
        for project in projects_root.iterdir():
            if project.is_dir() and project.name != "_template":
                shutil.rmtree(project)
        dashboard = self.run_cli("dashboard")
        self.assertEqual(dashboard.returncode, 0, dashboard.stdout + dashboard.stderr)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, "scripts/workspace.py", *arguments],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
        )

    def create_pdf(self, name="2603.99999v1.pdf"):
        path = Path(self.temporary_directory.name) / name
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        writer.add_metadata(
            {
                "/Title": "Test Archive Paper",
                "/Author": "Haiyue Zhang; Yi Nian; Yue Zhao",
                "/CreationDate": "D:20260325084249+08'00'",
            }
        )
        with path.open("wb") as handle:
            writer.write(handle)
        return path

    def test_empty_workspace_passes_check(self):
        result = self.run_cli("check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 个项目", result.stdout)

    def test_new_project_is_complete_and_updates_dashboard(self):
        result = self.run_cli(
            "new",
            "demo-project",
            "--title",
            "Demo Project",
            "--area",
            "research-infrastructure",
            "--owner",
            "Researcher",
            "--tag",
            "workspace",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        project = self.root / "projects" / "demo-project"
        metadata = jsonc_loads((project / "project.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["id"], "demo-project")
        self.assertEqual(metadata["title"], "Demo Project")
        self.assertEqual(metadata["tags"], ["workspace"])
        self.assertNotIn("{{", (project / "README.md").read_text(encoding="utf-8"))

        dashboard = (self.root / "dashboard" / "projects.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("[Demo Project](../projects/demo-project/README.md)", dashboard)

        check = self.run_cli("check")
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        self.assertIn("1 个项目", check.stdout)

    def test_invalid_slug_is_rejected_without_writes(self):
        result = self.run_cli("new", "Invalid Slug")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / "projects" / "Invalid Slug").exists())

    def test_invalid_project_reports_error_instead_of_crashing(self):
        result = self.run_cli("new", "broken-project")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        metadata_path = self.root / "projects" / "broken-project" / "project.json"
        metadata = jsonc_loads(metadata_path.read_text(encoding="utf-8"))
        del metadata["title"]
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        check = self.run_cli("check")
        self.assertEqual(check.returncode, 1)
        self.assertIn("project.json 缺少字段 title", check.stdout)
        self.assertNotIn("Traceback", check.stderr)

    def test_new_project_rolls_back_when_dashboard_update_fails(self):
        first = self.run_cli("new", "existing-project")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        metadata_path = self.root / "projects" / "existing-project" / "project.json"
        metadata = jsonc_loads(metadata_path.read_text(encoding="utf-8"))
        del metadata["title"]
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        second = self.run_cli("new", "rolled-back-project")
        self.assertEqual(second.returncode, 2)
        self.assertFalse((self.root / "projects" / "rolled-back-project").exists())

    def test_paper_add_archives_pdf_and_creates_records(self):
        project = self.run_cli("new", "agent-security")
        self.assertEqual(project.returncode, 0, project.stdout + project.stderr)
        source = self.create_pdf()

        result = self.run_cli(
            "paper",
            "add",
            str(source),
            "--project",
            "agent-security",
            "--priority",
            "high",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(source.exists(), "入库不得删除下载源文件")

        archived = (
            self.external_library
            / "papers"
            / "2026"
            / "2026-arxiv-zhang-test-archive-paper-2603.99999v1.pdf"
        )
        self.assertTrue(archived.is_file())
        self.assertEqual(source.read_bytes(), archived.read_bytes())

        bibliography = (self.root / "literature" / "bibliography.bib").read_text(
            encoding="utf-8"
        )
        self.assertIn("@misc{zhang2026testArchivePaper,", bibliography)
        self.assertIn("eprint = {2603.99999}", bibliography)
        self.assertIn("% sha256:", bibliography)

        catalog = jsonc_loads(
            (self.root / "literature" / "catalog.json").read_text(encoding="utf-8")
        )
        record = next(
            item
            for item in catalog["records"]
            if item["citationKey"] == "zhang2026testArchivePaper"
        )
        self.assertEqual(record["identifiers"]["arxiv"], "2603.99999")
        self.assertEqual(record["localFile"], str(
            Path("literature/files/papers/2026/2026-arxiv-zhang-test-archive-paper-2603.99999v1.pdf")
        ))
        self.assertEqual(record["sha256"], catalog["records"][-1]["sha256"])

        note = (
            self.root
            / "literature"
            / "reading-notes"
            / "2026-arxiv-zhang-test-archive-paper.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Project IDs: `agent-security`", note)
        self.assertIn("Reading status | `queued`", note)

        queue = (self.root / "dashboard" / "reading.md").read_text(encoding="utf-8")
        self.assertIn("2026-arxiv-zhang-test-archive-paper.md", queue)
        self.assertIn("| high | `agent-security` |", queue)
        self.assertLess(
            queue.index("2026-arxiv-zhang-test-archive-paper.md"),
            queue.index("状态建议使用"),
        )

    def test_paper_add_dry_run_does_not_write(self):
        source = self.create_pdf()
        bibliography = self.root / "literature" / "bibliography.bib"
        before = bibliography.read_text(encoding="utf-8")

        result = self.run_cli("paper", "add", str(source), "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("未写入任何文件", result.stdout)
        self.assertEqual(before, bibliography.read_text(encoding="utf-8"))
        self.assertEqual(list(self.external_library.rglob("*.pdf")), [])

    def test_paper_add_rejects_duplicate_arxiv_record(self):
        source = self.create_pdf()
        first = self.run_cli("paper", "add", str(source))
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)

        second = self.run_cli("paper", "add", str(source))
        self.assertEqual(second.returncode, 2)
        self.assertIn("BibTeX key 已存在", second.stderr)
        self.assertEqual(len(list(self.external_library.rglob("*.pdf"))), 1)


if __name__ == "__main__":
    unittest.main()
