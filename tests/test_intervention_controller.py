import unittest
from scripts.intervention_controller import approved_run_ids, validate_manual_resume

class InterventionControllerTests(unittest.TestCase):
    def test_only_explicitly_approved_intervention_issues_are_selected(self):
        issues=[
            {"number":1,"body":"Workflow run ID: 12345","labels":[{"name":"human-intervention"}]},
            {"number":2,"body":"Workflow run ID: 23456","labels":[{"name":"human-intervention"},{"name":"approved-to-resume"}]},
            {"number":3,"body":"Workflow run ID: 34567","labels":[{"name":"approved-to-resume"}]},
            {"number":4,"body":"No run identifier","labels":[{"name":"human-intervention"},{"name":"approved-to-resume"}]},
        ]
        self.assertEqual(approved_run_ids(issues),[(2,23456)])

    def test_manual_resume_requires_explicit_owner_note_and_numeric_run_id(self):
        self.assertIsNone(validate_manual_resume("12345","I approve retrying run 12345."))
        self.assertIsNotNone(validate_manual_resume("","I approve"))
        self.assertIsNotNone(validate_manual_resume("abc","I approve"))
        self.assertIsNotNone(validate_manual_resume("12345",""))

if __name__=="__main__":
    unittest.main()
