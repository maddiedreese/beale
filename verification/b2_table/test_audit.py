import unittest

try:
    from .audit import build_report, global_alignment
except ImportError:
    from audit import build_report, global_alignment


class B2TableAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report(trials=99, seed=20260801)

    def test_global_alignment_is_deterministic(self):
        result = global_alignment("abc", "axbc")
        self.assertEqual(result["score"], 2)
        self.assertEqual(result["right_only"], [1])

    def test_pursuing_is_not_admissible_deletion(self):
        supported = self.report["supported_local_interval"]
        self.assertEqual(supported["admissible_deleted_positions"], [242, 243, 244, 245, 246])
        self.assertNotIn(240, supported["admissible_deleted_positions"])

    def test_local_constraints(self):
        constraints = self.report["inferred_constraints"]
        self.assertEqual(constraints["number_241"]["observations"], {"i": 2})
        self.assertEqual(constraints["number_246"]["observations"], {"d": 3})

    def test_all_admissible_models_preserve_alphabet_episode(self):
        candidates = self.report["single_deletion_candidates_240_246"]
        episodes = {candidates[str(position)]["b1_positions_188_207"]
                    for position in range(242, 247)}
        self.assertEqual(episodes, {"abcdefghiijklmmnohpp"})

    def test_complete_b1_statistic(self):
        result = self.report["complete_b1_application"]
        self.assertEqual(result["representative_longest_walk"]["length"], 17)
        self.assertEqual(result["representative_longest_walk"]["start"], 188)
        self.assertEqual(result["representative_longest_walk"]["end"], 204)
        self.assertEqual(len(result["representative_rows"]), 520)
        self.assertEqual(result["positions_that_differ_across_admissible_models"], [347])
        self.assertEqual(
            [row["position"] for row in result["model_deltas_from_representative"]["242"]],
            [347],
        )

    def test_anchor_collision_policy_does_not_create_the_episode(self):
        result = self.report["printed_anchor_collision_sensitivity"]
        self.assertEqual(result["primary_policy"], "last_assignment_wins")
        self.assertEqual(result["first_assignment_longest_walk"]["length"], 17)
        self.assertEqual(result["last_assignment_longest_walk"]["length"], 17)

    def test_neighbor_edit_sensitivity_is_explicit(self):
        sensitivity = self.report["neighbor_number_error_sensitivity"]
        reconstructed = sensitivity["piecewise_reconstructed_table"]
        self.assertEqual([row["length"] for row in reconstructed], [17, 20, 21, 21])
        self.assertEqual(reconstructed[1]["edits"], [{
            "b1_position": 205,
            "printed_number": 301,
            "delta": 1,
            "replacement_number": 302,
        }])


if __name__ == "__main__":
    unittest.main()
