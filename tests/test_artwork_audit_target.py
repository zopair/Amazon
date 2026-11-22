import unittest

from scripts.artwork_audit_target import resolve_audit_theme, review_count


class ArtworkAuditTargetTests(unittest.TestCase):
    def test_pull_request_from_christmas_theme_selects_christmas(self):
        self.assertEqual(
            resolve_audit_theme(event_name="pull_request", head_ref="christmas-theme"),
            "christmas",
        )

    def test_follow_up_pull_request_targeting_christmas_theme_selects_christmas(self):
        self.assertEqual(
            resolve_audit_theme(event_name="pull_request", base_ref="christmas-theme"),
            "christmas",
        )

    def test_explicit_dispatch_theme_takes_precedence(self):
        self.assertEqual(
            resolve_audit_theme(
                requested_theme="flowers",
                event_name="pull_request",
                head_ref="christmas-theme",
            ),
            "flowers",
        )

    def test_unrelated_pull_request_keeps_existing_fruit_default(self):
        self.assertEqual(
            resolve_audit_theme(event_name="pull_request", head_ref="feature/other"),
            "fruit",
        )

    def test_fruit_pilot_remains_twelve_designs(self):
        self.assertEqual(review_count("fruit"), 12)

    def test_christmas_audit_covers_all_fifty_motifs(self):
        self.assertEqual(review_count("christmas"), 50)

    def test_unknown_theme_is_rejected(self):
        with self.assertRaises(ValueError):
            resolve_audit_theme(requested_theme="unknown")


if __name__ == "__main__":
    unittest.main()
