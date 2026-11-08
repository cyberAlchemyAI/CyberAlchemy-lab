import json
import unittest
from pathlib import Path


class TabletopTests(unittest.TestCase):
    def test_all_32_ids_map_once_to_unique_discriminators(self):
        path = Path(__file__).resolve().parents[1] / "fixtures/hostile/body-war-canary-tabletop-cases.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        cases = value["cases"]
        self.assertEqual([case["id"] for case in cases], [f"T{i:02d}" for i in range(1, 33)])
        self.assertEqual(len({case["discriminator"] for case in cases}), 32)
        self.assertEqual(value["authority_effect"], "none")
        for case in cases:
            self.assertTrue(case["classification"])
            self.assertTrue(case["discriminator"])


if __name__ == "__main__": unittest.main()
