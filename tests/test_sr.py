import unittest

from sr import schedule


class TestSchedule(unittest.TestCase):
    def test_correct(self):
        state = {"reps": 0, "interval_days": 0, "easiness": 2.5, "due_at": ""}
        out = schedule(state, 5)
        self.assertEqual(out["reps"], 1)
        self.assertEqual(out["interval_days"], 1)
        self.assertGreater(out["easiness"], 2.5)

    def test_incorrect(self):
        state = {"reps": 2, "interval_days": 6, "easiness": 2.5, "due_at": ""}
        out = schedule(state, 2)
        self.assertEqual(out["reps"], 0)
        self.assertEqual(out["interval_days"], 1)
        self.assertGreaterEqual(out["easiness"], 1.3)


if __name__ == "__main__":
    unittest.main()
