import json
import tempfile
import unittest
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("portfolio", ROOT / "scripts" / "build_commercial_portfolio.py")
portfolio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(portfolio)


class CommercialPortfolioTests(unittest.TestCase):
    def test_three_demos_and_no_fake_master(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = portfolio.build(Path(tmp))
            self.assertEqual(len(files), 9)
            for folder in Path(tmp).iterdir():
                manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
                self.assertIsNone(manifest["master_video"])
                self.assertFalse(manifest["approval"]["approved"])
                self.assertFalse(manifest["publishing"]["auto_ads"])
                self.assertEqual(manifest["production_status"], "PREPRODUCTION_ONLY")
                self.assertIn("00:00:00,000", (folder / "captions-draft.srt").read_text())

    def test_bad_claim_not_allowed(self):
        data = json.loads(portfolio.INPUT.read_text())
        campaign = data["campaigns"][1]
        campaign["scenes"][0]["voice"] = "Cura tu piel"
        with self.assertRaises(ValueError):
            portfolio.validate_campaign(campaign)

    def test_bad_path_rejected(self):
        data = json.loads(portfolio.INPUT.read_text())
        data["campaigns"][0]["id"] = "../escape"
        with self.assertRaises(ValueError):
            portfolio.validate_campaign(data["campaigns"][0])

    def test_invalid_timeline_rejected(self):
        data = json.loads(portfolio.INPUT.read_text())
        data["campaigns"][0]["scenes"][1]["start"] = 4
        with self.assertRaises(ValueError):
            portfolio.validate_campaign(data["campaigns"][0])


if __name__ == "__main__":
    unittest.main()
