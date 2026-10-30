"""Structure-only verification of design fixtures. Never claim MTProto runtime coverage."""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CASE_FILE = ROOT / "contracts" / "scenarios.v1.json"
ALLOWED_AREAS = {"listener","handshake","protocol","transport","routing","lifecycle","capacity","backpressure","shutdown","diagnostics","media","worker","ffi"}
ALLOWED_TIERS = {"protocol","unit","integration","load","future"}

class SpecContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(CASE_FILE.read_text(encoding="utf-8"))
        cls.cases = cls.doc["cases"]

    def test_version_and_disclaimer(self):
        self.assertEqual(self.doc["schema_version"], 1)
        self.assertIn("not proof", self.doc["purpose"].lower())

    def test_cases_are_unique_complete_and_nonexecuting(self):
        self.assertGreaterEqual(len(self.cases), 12)
        ids = [c["id"] for c in self.cases]
        self.assertEqual(len(ids), len(set(ids)))
        for c in self.cases:
            self.assertRegex(c["id"], r"^CORE-[0-9]{3}$")
            self.assertIn(c["area"], ALLOWED_AREAS)
            self.assertIn(c["tier"], ALLOWED_TIERS)
            for name in ("scenario","input","expected","failure"):
                self.assertIsInstance(c[name], str)
                self.assertGreater(len(c[name].strip()), 15)
            for forbidden in ("api.telegram.org", "workers.dev", "token=", "password="):
                self.assertNotIn(forbidden, (c["input"]+" "+c["expected"]).lower())

    def test_readme_is_not_a_false_green(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("no runnable", readme)
        self.assertIn("only validates", readme)
        self.assertTrue((ROOT / "docs" / "SECURITY_THREAT_MODEL.md").exists())
        self.assertTrue((ROOT / "docs" / "EXPERIMENTS.md").exists())

if __name__ == "__main__":
    unittest.main()
