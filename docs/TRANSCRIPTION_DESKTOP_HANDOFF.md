# Desktop transcription hardening — handoff

The canonical `scripts/transcribe_correct.py` now **returns exit code 1** if any scene fails transcription. It validates scene count and contiguous names, rejects empty scenes, removes stale HyperFrames temporary transcripts, persists `transcription-report.json`, and refuses to claim a clean pass when any source fails. No provider calls, no credits, no ads.

## Windows / Claude Code Desktop

From the repository root, with Python 3.11+, FFmpeg, Node/npm and the previously installed local HyperFrames CLI:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q tests/test_transcribe_fail_closed.py
python scripts/transcribe_correct.py --project .\storage\ugc-pilot\scenes --expected-scenes 6
```

Never run production transcriptions using placeholder MP4 files. CLI uses `npx --no-install` to avoid silent package downloads/installs; verify the installed HyperFrames executable supports that invocation in Desktop. If it fails, diagnose and explicitly provision the dependency before retrying.

**Pipeline contract:** after this script returns 0, downstream composition must still validate transcript timestamps, SRT extraction, captions against recorded audio and technical media properties. A successful transcript is not lip-sync validation and does not itself create `subtitles.srt`.

**Unaddressed:** atomic scene job receipt/idempotency and crash reconciliation in Higgsfield; six-beat planning preset; an end-to-end six-scene MP4 with captions and visual QA. Keep PR #11 and #12 separate until Desktop integration.

**Status:** code and automated tests published to feature branch. GitHub CI is the source of actual test evidence; do not claim real video QA from mocked unit tests.
