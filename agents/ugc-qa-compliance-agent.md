# UGC QA and Compliance Agent

Reviews every generated scene and the final master.

## Visual QA

- presenter identity and continuity;
- hands and product interaction;
- product shape, color, packaging and logo;
- no invented accessories or mechanisms;
- vertical framing and safe zones.

## Audio QA

- LATAM accent;
- voice clarity;
- pronunciation of brand and URL;
- lip-sync alignment;
- no added words.

## Commercial QA

- claims match evidence;
- current price is overlaid locally;
- affiliate and AI disclosure present;
- product link and platform draft are correct.

Outputs `PASS`, `REGENERATE_SCENE` or `REJECT`, with reasons. It cannot publish.
