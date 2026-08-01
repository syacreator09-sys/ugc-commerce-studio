---
name: create-ugc-product-campaign
description: Create a draft-only UGC campaign for an owned or affiliate product using Higgsfield.
allowed-tools: Bash, Read, Write
---

# Create UGC Product Campaign

1. Read `SKILL.md`, `config/policies.json` and the product input.
2. Run product validation and stop if rights, evidence or availability are missing.
3. Build the dynamic script and show it as a table.
4. Create the immutable plan and display its `scope_id`.
5. Do not generate until an approval matches that scope.
6. Run `scripts/run_higgsfield_pilot.py` after approval.
7. Review scenes, transcribe, caption, assemble and run QA.
8. Export draft-only package with affiliate link metadata and disclosures.

Never publish or activate ads.
