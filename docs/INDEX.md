# Index

Catalogue of every design document in this wiki. A document that is not listed here is invisible, so
index new ones as they are written.

The library is scaffolded and has no behaviour yet — see [progress.md](progress.md) for the milestone
log.

## Design

The library holds a type per kind of dungeon. Each type gets its own document; there is one type so
far.

| Document | What it covers |
|---|---|
| [design.md](design.md) | The library's shape, then `FixedRoomDungeon` — what a dungeon is in the world, the two wiring passes, and why the rooms are permanent |

## Process and discipline

| Document | What it covers |
|---|---|
| [test-plan.md](test-plan.md) | Every behaviour the library commits to covering and the test covering it. **Start here** — this is where behaviour is agreed |
| [progress.md](progress.md) | Reverse-chronological milestone log — what exists, with evidence |

## Integration

| Document | What it covers |
|---|---|
| [installing.md](installing.md) | What a game declares to run this library — written as each requirement is decided, so it grows with the machinery |
| [interoperability.md](interoperability.md) | This library against every sibling library in `libraries/` |

## Archive

Historical context, not authoritative. Material in [archive/](archive/) is preserved per the
"don't delete; supersede" principle. The archive is currently empty.
