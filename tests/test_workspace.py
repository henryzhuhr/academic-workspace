import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parent.parent


class WorkspaceCliTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "workspace"
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
        metadata = json.loads((project / "project.json").read_text(encoding="utf-8"))
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
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
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
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        del metadata["title"]
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        second = self.run_cli("new", "rolled-back-project")
        self.assertEqual(second.returncode, 2)
        self.assertFalse((self.root / "projects" / "rolled-back-project").exists())


if __name__ == "__main__":
    unittest.main()
