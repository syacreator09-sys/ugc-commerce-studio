# Santmun functional parity — audited baseline (2026-11-22)

## Reference verification

Source: public `santmun/ugc-ad-meta`, README, SKILL, scripts, prompts, workflow and repository tree read directly. README claims MIT, **but no LICENSE file appears in the inspected Git tree**. No external code, model pool images or demo MP4 copied. Do not infer that reference video assets are licensed.

| Capability | Santmun | UGC Commerce Studio main | State / action |
|---|---|---|---|
| Setup-once | config workflow | config/setup wizard | PARCIAL / verify real multi-brand configs |
| Six scenes / 30 sec | fixed six scenes | dynamic scenes | PARCIAL / separate parity preset required |
| Higgsfield | CLI, Kling/Seedance | Higgsfield guarded adapter | IMPLEMENTADO SIN PRUEBA INTEGRAL |
| Sequential retry | CLI backoff | sequential retry + scope approval | PARCIAL / receipts and crash recovery audit |
| Whisper | HyperFrames | transcribe_correct.py | PARCIAL / failure currently allows zero exit |
| Hard cuts | HyperFrames | concat FFmpeg | PARCIAL |
| Burned captions | HyperFrames example | existing build_composition.py concatenates only | AUSENTE in existing route; new optional compositor |
| QA video | example MP4 reported | incomplete objective QA | PARCIAL / new FFprobe gates |
| Creative intelligence | minimal | independent CI repo | IMPLEMENTADO SIN PRUEBA INTEGRAL |
| Visual 1:1 | sample MP4 referenced | no comparable real master | BLOQUEADO / consent + approved generation |

## New isolated compositor

```bash
python scripts/composite_verified.py --project path/to/scenes --subtitles path/to/subtitles.srt --require-captions --output path/to/master.mp4
```

Accepts `scene-1.mp4 ... scene-N.mp4` with contiguous numbering, **each containing audio + video**; normalizes geometry, fps and audio; hard-cut concat, optional burned captions with FFmpeg libass; verifies the rendered master with FFprobe; produces `qa-report.json`. `--require-captions` blocks uncaptained delivery. It does not call Higgsfield or modify the existing `build_composition.py`. These files are original implementations, not a source-code port.

## Verification and limitations

Developer executed a *separate prototype* locally with two synthetic 1-second clips: output 1080x1920, about 2.04 seconds, audio present, captions burn successful. That prototype is **not sufficient evidence for six-scene parity**, and this GitHub copy needs its own execution/CI check. Test cases in `tests/test_composite_verified.py` are **not executed on GitHub**. Mac/Windows escaping, black frames, audio loudness and visual continuity require additional checks.

Before claiming parity: run complete project regression suite, generate six authorized clips, time-sync real Whisper captions, compare against permissioned reference visually, validate file checksum, inspect portrait safe zones and lipsync. Do not spend credits or launch ads without approval.
