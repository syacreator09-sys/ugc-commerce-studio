"""Claude Code project skill packaging and no-cost safety references."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude" / "skills" / "cano-ugc-ads" / "SKILL.md"
REFERENCE = SKILL.parent / "references" / "production-workflow.md"


def test_skill_is_project_discoverable_and_declares_trigger():
    assert SKILL.is_file()
    content = SKILL.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    frontmatter = content.split("---\n", 2)[1]
    assert "name: cano-ugc-ads" in frontmatter
    assert "description:" in frontmatter
    assert "anuncios UGC" in frontmatter


def test_skill_reuses_existing_scripts_not_new_engine():
    content = SKILL.read_text(encoding="utf-8") + REFERENCE.read_text(encoding="utf-8")
    for path in [
        "scripts/export_ugc_ads_drafts.py",
        "scripts/build_six_scene_plan.py",
        "scripts/generate_ad.py",
        "scripts/transcribe_correct.py",
        "scripts/build_captions_srt.py",
        "scripts/composite_verified.py",
    ]:
        module_form = path.removesuffix(".py").replace("/", ".")
        assert path in content or module_form in content
        assert (ROOT / path).is_file()


def test_skill_has_explicit_safety_and_no_autopublish():
    content = SKILL.read_text(encoding="utf-8")
    assert "scope_id" in content
    assert "approval" in content.lower() or "aprobación" in content.lower()
    assert "No generar" in content
    assert "No hagas merge" in content
    assert "No dupliques" in content
    assert "FFprobe" in content
    assert "master.mp4" in content
