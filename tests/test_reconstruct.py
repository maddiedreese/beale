import unittest

from analysis.printed_label_collision import build_report


class ReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report()

    def test_frozen_cipher(self):
        self.assertEqual(self.report["cipher_count"], 520)

    def test_pursuing_is_printed_and_collision_is_visible(self):
        words = [event["word"].lower()
                 for event in self.report["label_240_assignments"]]
        self.assertEqual(words, ["pursuing", "invariably"])

    def test_prior_art_twenty_character_reconstruction(self):
        self.assertEqual(self.report["working_letters_188_207"],
                         "abcdefghiijklmmnohpp")

    def test_seventeen_character_walk(self):
        self.assertEqual(self.report["working_forward_walk"]["length"], 17)
        self.assertEqual(self.report["working_forward_walk"]["positions_1_based"],
                         [188, 204])
        self.assertEqual(self.report["working_forward_walk"]["text"],
                         "abcdefghiijklmmno")

    def test_four_changed_positions_in_walk(self):
        changed = [row for row in self.report["changed_positions"]
                   if row["b1_position"] <= 204]
        self.assertEqual(
            [(row["b1_position"], row["number"], row["ordinary_letter"],
              row["working_letter"]) for row in changed],
            [(189, 436, "l", "b"), (191, 320, "i", "d"),
             (199, 305, "p", "k"), (202, 461, "h", "m")],
        )


if __name__ == "__main__":
    unittest.main()
