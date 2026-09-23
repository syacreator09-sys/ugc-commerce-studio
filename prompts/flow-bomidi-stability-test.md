# Flow BOMIDI Stability Test Prompts

Status: EXPERIMENTAL

Use these prompts only with the test protocol in:
`docs/experiments/2026-09-23-flow-bomidi-stability-handoff.md`.

## FLOW-BOMIDI-FIDELITY-01 — Veo 3.1 Fast

Inputs:

- saved Influencer V2 Character;
- BOMIDI reference A: clean full product;
- BOMIDI reference B: clean front/detail product.

Settings:

```text
Veo 3.1 Fast
Ingredients
9:16
720p
8s
x1
Agent OFF
```

Prompt:

```text
Vertical 9:16 realistic UGC smartphone video.

Use @INFLUENCER_V2 as the consistent brunette UGC creator.
Use the uploaded product reference images as the same physical pink product.

Medium close-up in a warm bedroom with soft natural daylight.

The creator holds the referenced pink product upright beside her face with one hand.

She looks at the camera, blinks naturally and gives a subtle friendly smile.

The product remains stationary, unobstructed and fully visible throughout the entire shot.

Match the referenced product as closely as possible:
same overall silhouette,
same tall central cylindrical barrel,
same protective vertical guides,
same rose-gold metallic ring,
same two front control buttons,
same indicator lights,
same power button,
same proportions and pink finish.

Minimal body movement.
Single continuous shot.
Locked camera.

No product interaction.
No hair interaction.
No scene change.
No text.
No subtitles.
```

## PASS gate before any interaction prompt

Do not proceed to button or hair interaction unless all pass:

- exact product silhouette;
- exact guide topology;
- correct ring;
- correct two-button layout;
- stable indicator area;
- stable character identity;
- no product substitution.

## FLOW-BOMIDI-INTERACTION-01 — only after fidelity PASS

Objective: finger approaches the button without contact.

```text
Vertical 9:16 realistic UGC smartphone video.

Use @INFLUENCER_V2 as the consistent brunette UGC creator.
Use the uploaded product reference images as the same physical pink product.

Keep the referenced product stationary and fully visible.

The creator holds the product upright beside her face with one hand.
Her free hand slowly rises.
Her index finger points beside the upper front control button and stops just before touching it.

The product itself does not move.

Natural blinking and breathing.
Minimal motion.
Single continuous shot.
Locked camera.

Keep the product shape, protective guides, metallic ring, two front buttons, indicator lights and proportions consistent with the references.

No button press.
No hair interaction.
No product rotation.
No scene change.
No text.
No subtitles.
```

## Stop rule

If the stationary fidelity test fails, do not attempt interaction prompts in Flow.

Switch to hybrid production:
AI influencer + exact product insert + edit.
