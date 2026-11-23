import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("compositor", ROOT / "scripts" / "composite_verified.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CompositorTests(unittest.TestCase):
    def test_scene_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i in (2, 1):
                (Path(tmp) / f"scene-{i}.mp4").touch()
            self.assertEqual([x.name for x in mod.scene_files(Path(tmp))], ["scene-1.mp4", "scene-2.mp4"])

    def test_scene_gap_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "scene-2.mp4").touch()
            with self.assertRaises(ValueError):
                mod.scene_files(Path(tmp))

    def test_missing_captions_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "scene-1.mp4").touch()
            with patch.object(mod, "inspect", return_value={"duration": 1.0}):
                with self.assertRaises(FileNotFoundError):
                    mod.compose(Path(tmp), Path(tmp) / "master.mp4", subtitles=Path(tmp) / "missing.srt")

    def test_existing_scene_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            scene = Path(tmp) / "scene-1.mp4"
            scene.touch()
            with patch.object(mod, "inspect", return_value={"duration": 1.0}):
                with self.assertRaises(ValueError):
                    mod.compose(Path(tmp), scene)


if __name__ == "__main__":
    unittest.main()
