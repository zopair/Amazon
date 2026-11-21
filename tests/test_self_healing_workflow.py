from pathlib import Path
import unittest


class SelfHealingWorkflowDependencyTests(unittest.TestCase):
    def test_pinned_dependencies_are_installed_before_python_tasks(self):
        workflow_path = Path(".github/workflows/kdp-self-healing-inspector.yml")
        requirements_path = Path("requirements.txt")

        self.assertTrue(workflow_path.is_file())
        self.assertTrue(requirements_path.is_file())

        workflow = workflow_path.read_text(encoding="utf-8")
        setup_python = workflow.find("- name: Set up Python")
        install_dependencies = workflow.find(
            "python -m pip install --disable-pip-version-check -r requirements.txt"
        )
        classify_logs = workflow.find("python scripts/kdp_inspector.py")
        run_repairs = workflow.find("python scripts/repair_engine.py")
        run_tests = workflow.find("python -m unittest discover -s tests -t . -v")

        self.assertGreaterEqual(setup_python, 0, "Python setup step is missing")
        self.assertGreater(install_dependencies, setup_python,
                           "Pinned dependencies must be installed after Python setup")
        self.assertGreater(classify_logs, install_dependencies,
                           "Log classification must run after dependency installation")
        self.assertGreater(run_repairs, install_dependencies,
                           "Repair engine must run after dependency installation")
        self.assertGreater(run_tests, install_dependencies,
                           "Regression tests must run after dependency installation")


if __name__ == "__main__":
    unittest.main()
