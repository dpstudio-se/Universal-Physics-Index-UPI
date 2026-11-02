import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prompt_master import generate


class PromptMasterTests(unittest.TestCase):
    def test_ci_has_bounded_loop(self):
        content = generate("Repair UPI", mode="ci")
        self.assertIn("maximum 3 cycles", content)
        self.assertIn("Do not merge automatically", content)
        self.assertIn("fail closed", content)

    def test_general_prompt_keeps_evidence_boundary(self):
        content = generate("Research task")
        self.assertIn("experimental scientific verification", content)
        self.assertIn("untrusted", content)

    def test_invalid_goal_or_mode_fails(self):
        with self.assertRaises(ValueError):
            generate(" ")
        with self.assertRaises(ValueError):
            generate("A", mode="unknown")


if __name__ == "__main__":
    unittest.main()
