# evennia-procedural-dungeons

Procedural dungeons for [Evennia](https://www.evennia.com/). The library holds a type per kind of
dungeon; they are not required to work alike.

**`FixedRoomDungeon`** is the first. It periodically rewires the exits between a fixed set of rooms, so
the route through them cannot be memorised. The rooms are ordinary world content — built once, by
whatever builds the rest of your world, and permanent. On a cycle the type deletes the exits it
previously made and draws a fresh route between two fixed ends, optionally wiring the spare directions
into one-way loops. A player who learned the way through last week has to work it out again, and the
game loses no content to do it.

## Status

**Scaffolded, no behaviour.** The repo structure, test runner and documentation surfaces exist. No
dungeon type is written yet: `FixedRoomDungeon`'s algorithm is agreed and written up, the test plan is
next. Nothing is installable-and-useful. See [docs/progress.md](docs/progress.md).

## Is it for me?

`FixedRoomDungeon` probably suits you if you want part of your world to stay explorable rather than
becoming a walk-through-it alias, and you are willing to author the rooms yourself.

It probably does not if you want a generator that invents rooms. This type creates and deletes exits
only — rooms are yours, they are permanent, and nothing a player is standing in ever disappears. That
constraint is the design, not a limitation of it. A future type may work differently; nothing here
rules that out.

## How it fits together

- You author the rooms and tag them: `dungeon_room`, `dungeon_anchor`, both keyed by a dungeon id.
- You construct a `FixedRoomDungeon` with that id, how many rooms the route should run through, and
  whether spare directions get filled.
- You call `rewire()` on whatever schedule you like. The library owns no clock and reads no settings.

## Install

Nothing is published. See [docs/installing.md](docs/installing.md).

## Learn more

- [docs/design.md](docs/design.md) — the rewire algorithm, and why the rooms are permanent.
- [docs/test-plan.md](docs/test-plan.md) — every behaviour the library commits to.
- [docs/INDEX.md](docs/INDEX.md) — the full design wiki.

## License

BSD 3-Clause. See [LICENSE](LICENSE).
