# Progress

Running log of milestones with links to evidence. Reverse chronological — newest first.

## 2026-09-13 — scaffolded, first type's design agreed

1 test, passing. The repo carries the standard library shape and nothing else.

- **The library holds a type per kind of dungeon**, and they are not required to work alike. Nothing
  is promised library-wide that a future type might want to break — a later one generating rooms on
  traversal and collapsing behind the players stays possible.
- **`FixedRoomDungeon` is the first type** and its algorithm is agreed, written up in
  [design.md](design.md): permanent tagged rooms, two anchors, a spine drawn without replacement,
  leftover rooms attached two-way, and an optional one-way fill pass that never touches an anchor at
  either end.
- **A consumer constructs a frozen dataclass and calls `rewire()`** — `dungeon_id`, `spine_length`,
  `fill`, `directions`.
- **The library reads no settings and owns no clock.** Nothing to check at boot; validation happens at
  the start of a run, when the world exists. FCM will drive the cadence from `evennia-calendar`
  signals, with no dependency declared either way.
- **Identification is three tag categories**, keyed by the dungeon id — `dungeon_room`,
  `dungeon_anchor`, `dungeon_exit`. Declared in `config.py`.
- **No code yet.** No dungeon type is written; the next step is the test plan.
- Open: how the `directions` field is spelled, given it has to carry opposites. Marked `[TBD]` in
  [test-plan.md](test-plan.md).
