# CLAUDE.md

> **Project-wide working rules and cross-repo context live in the FCM umbrella repo's `CLAUDE.md`**,
> loaded automatically when you work from the umbrella root. If you opened this repo directly instead
> of via the umbrella, relaunch from the umbrella root for the full context. This file holds only this
> repo's specific instructions.

Instructions for Claude (and other LLM agents) working in this repository.

## What this project is

`evennia-procedural-dungeons` holds whatever kinds of procedural dungeon we end up building for
[Evennia](https://www.evennia.com/). Each kind is its own type in its own module; they are not
required to work alike.

**`FixedRoomDungeon` is the first and currently the only one.** It periodically rewires the exits
between a fixed set of rooms. The rooms are ordinary world content and never move; what changes on a
cycle is which direction leads where, so a route cannot be memorised — a player who learned the way
through last week has to work it out again, and the game loses no content to do it.

Other types may work completely differently — generating rooms on traversal, collapsing when the last
player leaves. Nothing here forecloses that. What each type promises is stated on the type, not on the
library.

FullCircleMUD is the intended first consumer.

For the big-picture overview, read [README.md](README.md).
For the design wiki, read [docs/INDEX.md](docs/INDEX.md).

## Project status

**Scaffolded, no behaviour.** The repo structure, test runner and docs surfaces exist; no dungeon type
is written yet. `FixedRoomDungeon`'s algorithm is agreed and written up in
[docs/design.md](docs/design.md). The next step is the test plan, then the tests, then the code. See
[docs/progress.md](docs/progress.md).

## Where to read first

1. [docs/test-plan.md](docs/test-plan.md) — the cases the library commits to. **A behavioural change
   starts here**, not in the code. **Start here.**
2. [docs/design.md](docs/design.md) — the rewire algorithm, as agreed.
3. [README.md](README.md) — what the library is and its status.
4. [docs/INDEX.md](docs/INDEX.md) — map of all design docs.
5. [docs/interoperability.md](docs/interoperability.md) — this library against its siblings.

## Load-bearing architectural principles

Every implementation decision must respect them.

1. **The library does not own game concepts.** Rooms, their descriptions, what lives in them, what a
   dungeon is *for* — all the consumer's. The library owns the connections between rooms and nothing
   else.

2. **No FCM-specific assumptions.** FullCircleMUD is the first consumer, not the specification. Its
   terrain types, its cartography, its combat — none of it belongs here.

3. **Test-first.** A case lands in [docs/test-plan.md](docs/test-plan.md), then the test, then the
   code. See [test-first-process.md](../../design/test-first-process.md) for the process and the
   rationale.

4. **A library of types, not a type.** Each kind of dungeon is its own module and its own class, and
   they are not required to work alike. Nothing is declared library-wide that a future type might
   reasonably want to break. `FixedRoomDungeon` is the first; a later one generating rooms on
   traversal and collapsing behind the players would be a legitimate sibling, not a contradiction.

5. **A type only ever deletes what it created.** Everything a type makes is tagged as it is made, and
   it deletes by that tag and by nothing else. Consumer-authored world content — the anchors' ways out
   into the wider world, an exit someone wrote in YAML — is never touched. This one *is* library-wide:
   it holds however a type works.

6. **No base class until there is a second type to extract against.** A base lifted from one
   implementation is a guess about the second. `FixedRoomDungeon` is written self-contained; the
   refactor happens when there is something real to share.

### FixedRoomDungeon's own promises

Properties of this type, not the library. A different type is free to break them.

- **It never creates or deletes a room.** Rooms are the consumer's world content and they are
  permanent. This is what the whole design rests on: nothing a player is standing in can vanish, so
  there is no instance lifecycle, no orphan, and no collapse to race against. A change that has
  `FixedRoomDungeon` creating rooms is not an optimisation, it is a different type.
- **Every room ends a rewire with at least one outbound exit.** A room the generator leaves
  unreachable-from is a player stuck until the next cycle.

## Out of scope

Decided as questions arise. Rulings so far:

- **The library owns no tables.** A `FixedRoomDungeon` is not stored; it is whatever carries its tags.
  The rooms and exits are Evennia objects, which are in the consumer's game database by definition. No
  alias, no router, no migration. Revisit if a future type gains data of its own that must outlive a
  rebuild.
- **The library owns no clock.** A type exposes the call; what triggers it is the consumer's. FCM
  drives it from `evennia-calendar` signals, which is convenient rather than required — no dependency
  either way, and a consumer wanting a plain `LoopingCall` writes one.
- **The library reads no settings.** Everything a type needs is either in the object the consumer
  constructed or resolvable from tags. There is no boot check because there is nothing to check at
  boot; validation happens at the start of a run, when the world exists.

## Working conventions

- **Behavioural change starts in the test plan.** Add the case, write the test, then implement. Fill
  the **Test function** column when the test exists — it is a coverage claim and the linter checks it
  both ways.
- **Editing design docs.** Update or add design documents whenever an architectural decision is made
  or refined. Capture the *why*, not just the *what*. Index new docs in [docs/INDEX.md](docs/INDEX.md).
- **Don't put implementation detail in this file or README.** Link out to `docs/` instead. Keep
  `CLAUDE.md` and `README.md` stable; let `docs/` churn.
- **License.** BSD 3-Clause. Source files carry an SPDX header on the first line
  (`# SPDX-License-Identifier: BSD-3-Clause`).

## Documentation discipline (load-bearing)

Design documents in `docs/` must reflect decisions **actually discussed and agreed on with the project
owner**. They are not a place to forward-design the system from first principles or extrapolate
"reasonable defaults" from a starting point.

**Rules:**

1. **Only capture what was discussed and agreed.** If the conversation establishes a principle, do not
   extrapolate it into specifics that were not raised — setting names, cycle periods, room counts, API
   shapes.
2. **Flag open questions explicitly.** Write `[TBD — needs discussion: <what is open>]` so a future
   session picks the topic up deliberately rather than inheriting an unagreed assumption.
3. **Smaller is better.** Three discussed points captured faithfully beat three discussed points plus
   seven invented ones. Resist filling out sections "for completeness".

**The tempting source of unasked-for answers is the wider procedural-generation literature.** BSP,
cellular automata, Delaunay triangulation, graph grammars — all were surveyed and all were set aside,
because a MUD room is a graph node and this design needs no geometry at all. A technique lifted from
that literature is an invention unless it has been discussed here.

## Repository layout

```
evennia-procedural-dungeons/
├── CLAUDE.md                  # this file
├── README.md
├── LICENSE                    # BSD 3-Clause
├── pyproject.toml
├── runtests.py                # standalone test runner; no gamedir required
├── .gitignore
├── docs/                      # design wiki (humans + LLMs)
│   ├── INDEX.md
│   ├── design.md              # the rewire algorithm, as agreed
│   ├── installing.md          # what a consumer declares; grows as we decide
│   ├── progress.md
│   ├── test-plan.md
│   ├── interoperability.md
│   └── archive/               # historical context, not authoritative
├── src/
│   └── evennia_procedural_dungeons/   # library code (src layout)
│       ├── __init__.py
│       ├── apps.py            # AppConfig; nothing runs at boot
│       ├── config.py          # the tag categories
│       ├── log.py             # binds dungeons_log via evennia-logging-extension → dungeons.log
│       └── tests.py           # unit tests, run via runtests.py
└── tests/                     # standalone test infrastructure
    ├── __init__.py
    ├── test_settings.py
    └── urls.py
```

**One module per dungeon type**, named for what distinguishes it. `FixedRoomDungeon` lands in
`fixed_rooms.py` when it is written — rooms fixed, wiring not. A later type goes in its own module on
the same axis, and nothing has to move.

No `contrib/` — nothing opt-in exists, and the standards forbid scaffolding one empty. No `examples/`
yet, for the same reason: there is nothing to demonstrate.

Development venv at `venv/`, gitignored.

## Tools and environment

- Python 3.10+ (pinned via `pyproject.toml`).
- Evennia and `evennia-logging-extension` are the runtime dependencies.
- **Tests use Django's test runner** via `python runtests.py`, which bootstraps Django then calls
  `evennia._init()`, as the siblings do. Not pytest, and no gamedir required.
- Development uses a dedicated venv at `venv/` (gitignored), independent of any consumer game.

## Sibling libraries to reference

- **[../evennia-survival/](../evennia-survival/)** — the reference shape for repo structure, the test
  runner and the docs surfaces. Owns no tables either, for the same kind of reason.
- **[../evennia-world-builder/](../evennia-world-builder/)** — builds the rooms a consumer tags into a
  dungeon. What this library rewires, that one authored.
