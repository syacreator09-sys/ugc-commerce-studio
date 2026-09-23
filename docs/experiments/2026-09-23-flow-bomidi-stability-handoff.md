# Flow UGC + BOMIDI — Stability Test Handoff

**Date:** 2026-09-23  
**Status:** EXPERIMENTAL / NOT CANONICAL  
**Scope:** Google Flow / Omni / Veo 3.1 experiments for a virtual UGC influencer presenting the BOMIDI HC02 pink automatic hair curler.

> This document records experiment results only. It does **not** replace the repository's current canonical Higgsfield production path.

## Goal

Find a stable workflow for:

- one reusable virtual UGC influencer;
- one exact physical product reference;
- vertical 9:16 social video;
- natural UGC behavior and speech;
- minimal identity drift;
- minimal product geometry drift;
- eventual product demo, hooks and CTA.

Target product used in this test:

- **BOMIDI HC02 / HC02_RS**
- pink automatic hair curler
- key visual traits:
  - pale pink body;
  - tall central cylindrical barrel;
  - protective vertical guides around the barrel;
  - rose-gold metallic ring;
  - two front control buttons;
  - indicator lights;
  - power button;
  - cable.

## Important distinction discovered

Three separate problems must be tested independently:

1. **Character identity stability**
2. **Product fidelity**
3. **Hand/product interaction**

A model can pass one and fail the others.

Do not treat “the woman stayed consistent” as proof that the product is correct.

---

## Assets used

### Original influencer attempt — REJECTED

The first brunette character looked natural and attractive for UGC, but Flow repeatedly triggered a false-positive style policy error related to “famous people” when the saved Character was used.

Observed behavior:

- original uploaded/generated character as a saved Flow Character: **blocked**
- same character without product: **still blocked**
- conclusion: issue was associated with the Character/likeness, not the BOMIDI product.

Decision:

- **Do not continue using original Luna character.**
- Do not spend more credits changing only the video model.

### New influencer V2 — PASS

A new clearly synthetic brunette influencer was generated.

Visual traits:

- brunette / warm brown hair;
- light hazel-green eyes;
- freckles / natural skin texture;
- white fitted ribbed top;
- light gray lounge pants;
- warm neutral bedroom;
- beauty/lifestyle UGC look.

Reference set:

- portrait image;
- full-body image.

Result:

- generated successfully in Flow;
- no famous-person block;
- face/hair/outfit/background remained stable in a solo video;
- natural blinking, facial expression and selfie-style movement worked.

**Current character conclusion:** PASS.

Suggested working name in notes: **Lina V2 / UGC Influencer V2** until a final canonical name is chosen.

---

## Voice experiment

Base voice considered:

- **Leda**
- female;
- youthful;
- mid-high pitch.

Custom performance text used / recommended:

```text
Young female UGC creator, warm and natural. Speak fluent Mexican Spanish with a neutral Mexico City accent. Conversational, confident and friendly, as if recommending a beauty product to a friend. Medium-soft voice, natural pacing, subtle smile, clear pronunciation. Avoid announcer style, exaggerated enthusiasm, robotic rhythm, Spain Spanish accent, or overly seductive delivery.
```

Example dialogue:

```text
Te enseño rápido esta rizadora automática. Se ve bonita, práctica y súper fácil de usar.
```

Status:

- voice setup created;
- preview behavior was inconsistent in UI;
- do **not** consider voice quality fully validated yet;
- validate audio only after visual stability is acceptable.

---

# Model test history

## 1. Veo 3.1 Lite — Frames / Start-End

### Method

- generated start and end images;
- asked Veo to interpolate;
- product held by influencer;
- small pose change.

### Result

FAIL for exact product fidelity.

Observed:

- influencer relatively stable;
- BOMIDI guides changed topology;
- vertical guides became horizontal/ring-like structures;
- buttons/geometry changed;
- model appeared to morph between endpoints rather than preserve one rigid product.

Lesson:

- Start + End frames are useful for transition endpoints;
- they are **not sufficient** to lock an exact commercial product through the entire interpolation;
- independently generated start/end images can themselves introduce geometry differences.

---

## 2. Veo 3.1 Fast — First Frame only

### Method

- first frame only;
- product nearly static;
- free finger approaches control button;
- prompt explicitly requested rigid product geometry.

### Result

FAIL for product topology.

Observed:

- drift started early;
- product geometry changed even before meaningful interaction;
- protective guides were reinterpreted;
- decreasing motion did not solve the product reconstruction issue.

Lesson:

- the failure was not caused only by the end frame;
- a generated first frame alone is not a strong enough anchor for exact product structure.

---

## 3. Veo / Ingredients tests

### Intended correction

Use:

- saved Character for woman;
- clean product references as Ingredients;
- no generated composite product as the primary source.

Google Flow guidance supports Ingredients as the reference mechanism for consistent characters/objects across clips.

However, the first character caused policy blocking, which prevented a clean controlled test.

Status:

- must be retested with **Influencer V2**, not the rejected original Luna.

---

## 4. Omni 1.1 Flash — Influencer only

### Result

PASS.

Observed in solo creator clip:

- face stable;
- hair stable;
- bedroom stable;
- natural blinking;
- natural head movement;
- believable selfie/UGC feeling.

This established that Influencer V2 is usable.

---

## 5. Omni 1.1 Flash — Influencer + BOMIDI

### Result

PARTIAL PASS.

What passed:

- influencer identity;
- facial expression;
- lip movement;
- background;
- general UGC vibe;
- temporal stability.

What failed:

- the generated object was **not the exact BOMIDI**;
- product was wrong from near the beginning rather than drifting only later;
- model generated a product inspired by the reference;
- head geometry, guides, controls and front layout did not match the real product.

Important conclusion:

> Omni is currently strong enough for the creator, acting, lips and UGC feel, but product fidelity remains the bottleneck.

---

# Current state

## Character

**PASS**

Do not generate another influencer unless V2 later shows a new critical failure.

## Product fidelity

**FAIL / unresolved**

The main remaining issue is not human identity.

## Hand-product interaction

**NOT READY**

Do not test button pressing or hair curling until the model can first reproduce the product correctly while stationary.

## Voice

**PARTIAL / not fully validated**

Do not optimize voice before visual product fidelity.

---

# Rules for the next session

1. **Do not regenerate the influencer.**
2. Use **Influencer V2** only.
3. **Agent OFF** for controlled model tests.
4. Test one variable at a time.
5. Product stays stationary first.
6. No hair interaction.
7. No button pressing.
8. No large wrist rotation.
9. No multi-scene prompt.
10. Do not infer that a “similar pink curler” is acceptable.
11. Compare exact:
   - central barrel;
   - protective guides;
   - rose-gold ring;
   - two buttons;
   - indicators;
   - power button;
   - overall silhouette.
12. Save a PASS only if product identity is recognizable as the same exact unit.

---

# Next recommended experiment

## Test ID: FLOW-BOMIDI-FIDELITY-01

### Model

**Veo 3.1 Fast**

Reason:

- character has already passed in Omni;
- next unresolved variable is product fidelity;
- Fast should be tested manually with clean product references before spending on higher-cost final-quality generation.

### Flow mode

**Video → Ingredients**

### Inputs

Use:

1. **Influencer V2 saved Character**
2. **Product reference A**
   - crop of the exact BOMIDI only;
   - product fully visible;
   - clean/plain background;
   - no box if possible.
3. **Product reference B**
   - same exact product;
   - front/detail view;
   - buttons + guides + metallic ring clearly visible.

Do not use:

- old Luna;
- generated composite woman + product images;
- mismatched product versions;
- package-only photo as the sole reference;
- extra background/style references.

### Settings

```text
model: Veo 3.1 Fast
mode: Ingredients
aspect_ratio: 9:16
resolution: 720p
duration: 8s
outputs: 1
agent: OFF
audio: optional OFF for this test
```

### Prompt

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

### PASS criteria

All must pass:

- [ ] influencer remains recognizable and stable;
- [ ] exact tall barrel shape retained;
- [ ] protective guides remain vertical and correctly arranged;
- [ ] rose-gold ring stays in correct location;
- [ ] two front buttons remain two;
- [ ] indicator placement is credible;
- [ ] product does not become a generic/different curler;
- [ ] no hand deformation that covers key geometry.

### FAIL condition

If Fast again generates a different product while stationary:

**Stop testing precise BOMIDI interaction in Flow.**

Do not escalate blindly to expensive Quality generation expecting a magic fix.

---

# Fallback production architecture if Fast fails

Use a hybrid ad:

```text
AI influencer / talking head
→ cut
→ real/static/product-faithful BOMIDI close-up
→ cut
→ influencer reaction / hook / CTA
```

This avoids asking a video generator to solve:

- exact rigid product topology;
- exact fingers;
- exact button contact;
- exact mechanical hair interaction;

all inside one generative shot.

Possible product shots can come from:

- original product photography;
- controlled image animation with minimal motion;
- compositing in post;
- another model specifically tested for strong reference adherence.

Candidates to evaluate later:

- Higgsfield / Seedance direct-scene;
- other reference-to-video models already available in the stack.

Do not assume another provider wins until tested with the exact same reference set and PASS criteria.

---

# Production design lesson

A commercial UGC ad does **not** need one model to perform the entire ad.

Preferred modular structure:

```text
HOOK / TALKING HEAD
→ PRODUCT INSERT
→ DEMO OR SIMULATED ACTION
→ RESULT
→ CTA
```

For the BOMIDI specifically:

- use influencer generation where human performance is valuable;
- use exact-source imagery where product geometry matters;
- only attempt full hand/hair demo after product fidelity passes.

---

# Current decision table

| Component | Status | Current best |
|---|---|---|
| Influencer identity | PASS | Influencer V2 |
| Natural UGC feel | PASS | Omni 1.1 |
| Facial movement | PASS | Omni 1.1 |
| Lip movement | PASS/PARTIAL | Omni 1.1 |
| Voice | PARTIAL | Leda custom |
| BOMIDI exact geometry | FAIL | unresolved |
| Button interaction | NOT READY | do not test yet |
| Hair interaction | NOT READY | do not test yet |
| Veo Frames | FAIL for exact product | do not use as product-lock solution |
| Flow Agent | useful for ideation, not controlled tests | OFF during benchmarks |
| Next benchmark | READY | Veo 3.1 Fast + Character + 2 clean product Ingredients |

---

# Session restart prompt

Use this in a new chat/session:

```text
Continue the Flow UGC BOMIDI stability experiment from:
docs/experiments/2026-09-23-flow-bomidi-stability-handoff.md

Do not restart the research or regenerate the influencer.

Current state:
- Influencer V2 is approved and works in Flow.
- Original Luna character was rejected after repeated famous-person false-positive blocking.
- Omni 1.1 produces a stable, natural influencer but recreates the BOMIDI inaccurately.
- Veo Lite/Fast frame-based tests also changed BOMIDI geometry.
- The unresolved problem is exact product fidelity, not character identity.
- Do not test button pressing or hair interaction yet.
- Next controlled test is FLOW-BOMIDI-FIDELITY-01:
  Veo 3.1 Fast, manual, Ingredients, 9:16, 720p, 8s, x1, Agent OFF,
  Influencer V2 + two clean BOMIDI product references,
  product stationary.

Read the handoff first, preserve the PASS/FAIL criteria, and continue from the next experiment only.
```

---

# Repository policy

This experiment remains **non-canonical** until a production path passes the product fidelity gate.

Do not remove or replace the repository's Higgsfield-only production rule solely because of these Flow experiments.

A provider change requires:

1. controlled comparison;
2. repeatable product fidelity;
3. character stability;
4. acceptable cost;
5. QA approval.
