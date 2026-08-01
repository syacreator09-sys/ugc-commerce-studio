# Claude Code instructions

When the user asks for UGC:

1. Read `SKILL.md` and `AGENTS.md`.
2. Run the setup workflow if `config/user-config.json` is missing.
3. Import and validate the product.
4. Show the script and plan before spending credits.
5. Request approval for the exact `scope_id`.
6. Use `scripts/run_higgsfield_pilot.py` or the CLI.
7. Never publish automatically.

Higgsfield is the only premium provider. It generates the avatar/presenter, acting, voice, audio, lip-sync and video. FFmpeg/HyperFrames are post-production tools only.
