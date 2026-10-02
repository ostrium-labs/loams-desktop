import unittest
from pathlib import Path

from required_workflows import matching_glob, matches_pull_request, selected_workflows, runs_complete


class RequiredWorkflowsTests(unittest.TestCase):
    def test_globs_follow_github_path_boundaries(self):
        self.assertTrue(matching_glob("crates/**", "crates/harness/src/lib.rs"))
        self.assertFalse(matching_glob("crates/*", "crates/harness/src/lib.rs"))
        self.assertTrue(matching_glob("**/*.md", "docs/setup/readme.md"))

    def test_desktop_paths_select_only_applicable_workflows(self):
        root = Path(__file__).resolve().parents[2]
        active = {str(p.relative_to(root)) for p in (root / ".github/workflows").glob("*.yml")}
        self.assertEqual(
            selected_workflows(root, "pull_request", "dev", ["CONTRIBUTING.md"], active),
            {".github/workflows/dco.yml"},
        )
        selected = selected_workflows(root, "pull_request", "dev", ["crates/harness/src/lib.rs"], active)
        self.assertIn(".github/workflows/ui-tests.yml", selected)
        self.assertIn(".github/workflows/windows.yml", selected)
        self.assertIn(".github/workflows/cursor-compatibility.yml", selected)
        self.assertNotIn(".github/workflows/linux-installer.yml", selected)
        push = selected_workflows(root, "push", "dev", ["crates/harness/src/lib.rs"], active)
        self.assertIn(".github/workflows/ui-tests.yml", push)
        self.assertIn(".github/workflows/windows.yml", push)

    def test_incomplete_or_failed_expected_run_cannot_pass(self):
        expected = {".github/workflows/ui-tests.yml", ".github/workflows/dco.yml"}
        ui = {"path": ".github/workflows/ui-tests.yml@refs/heads/dev", "status": "completed", "conclusion": "success"}
        dco = {"path": ".github/workflows/dco.yml", "status": "in_progress", "conclusion": None}
        self.assertEqual(runs_complete(expected, [ui]), (False, None))
        self.assertEqual(runs_complete(expected, [ui, dco]), (False, None))
        dco["status"] = "completed"
        dco["conclusion"] = "failure"
        self.assertEqual(runs_complete(expected, [ui, dco]), (False, ".github/workflows/dco.yml: failure"))
        dco["conclusion"] = "success"
        self.assertEqual(runs_complete(expected, [ui, dco]), (True, None))

    def test_fork_runs_without_pull_request_entries_match_the_head_repository(self):
        payload = {"number": 7, "pull_request": {"base": {"sha": "base"}, "head": {"ref": "fix", "repo": {"full_name": "contributor/loams-desktop"}}}}
        run = {"pull_requests": [], "head_branch": "fix", "head_repository": {"full_name": "contributor/loams-desktop"}}
        self.assertTrue(matches_pull_request(run, payload))
        run["head_repository"]["full_name"] = "someone-else/loams-desktop"
        self.assertFalse(matches_pull_request(run, payload))
        run["pull_requests"] = [{"number": 7, "base": {"sha": "base"}}]
        self.assertTrue(matches_pull_request(run, payload))
        run["pull_requests"][0]["base"]["sha"] = "old-base"
        self.assertFalse(matches_pull_request(run, payload))


if __name__ == "__main__":
    unittest.main()
