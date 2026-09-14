# Design

How the library is put together, and why. Everything here was agreed in conversation; open questions
carry `[TBD]`.

## The library holds types, not a type

Each kind of procedural dungeon is its own module and its own class. They are not required to work
alike, and nothing is promised library-wide that a future type might reasonably want to break. A later
type that generates rooms on traversal and collapses behind the players would be a legitimate sibling
of what is described below, not a contradiction of it.

**`FixedRoomDungeon` is the first and currently the only type.** Everything from here down is about
it. A second type gets its own document.

No base class exists and none is planned yet — one lifted from a single implementation is a guess
about the second. The refactor happens when there is something real to share.

## FixedRoomDungeon

The rooms are permanent world content. What changes on a cycle is the wiring between them.

### The object the consumer builds

A frozen dataclass. Frozen because `rewire()` mutates the world, never the configuration — and a
`Dungeon` handed to a signal receiver at boot should not be alterable afterwards.

| Field | What it is |
|---|---|
| `dungeon_id` | The key on all three tag categories. The only thing the consumer declares twice — once here, once in the world content |
| `spine_length` | How many pool rooms the route runs through between the anchors |
| `fill` | Whether spare directions get one-way exits |
| `directions` | The compass this dungeon uses, carrying opposites — four points for a wood, eight with diagonals, plus up and down for a mine |

`directions` carries opposites rather than bare names because pass one is reciprocal: a spine exit
north from one room needs a return exit south from the next.

### What a dungeon is, in the world

Not an object. It is whatever carries the tags with this `dungeon_id`.

| Tag category | On | What it means |
|---|---|---|
| `dungeon_room` | rooms | a room the route may be drawn through |
| `dungeon_anchor` | rooms | one of the two fixed ends. Exactly two per dungeon |
| `dungeon_exit` | exits | this type made it, so this type may delete it |

The categories are library constants; only the key varies, so adding a dungeon is one new id and no
new vocabulary.

The anchors are deliberately **not** tagged `dungeon_room`. An anchor is an endpoint, never a draw
candidate, and disjointness is what makes that true without a special case anywhere in the generator.

There is no start and no end. The generator picks either anchor and builds to the other; the result is
the same dungeon either way, because the route is bidirectional and the fill exits are
direction-neutral.

### The rewire, step by step

`rewire()` is a method on the dataclass. Who does each step — **[library]** for this library,
**[consumer]** for the game. No gaps in the algorithm itself.

- **[consumer]** authors the rooms and tags them, in whatever builds the rest of their world
- **[consumer]** constructs the dungeon and calls `rewire()` on whatever schedule they want
- **[library]** resolves the tags: the pool, the two anchors, the exits it made last time
- **[library]** validates what came back, and refuses loudly rather than half-building
- **[library]** deletes every exit tagged `dungeon_exit` with this id, one at a time
- **[library]** picks either anchor to start from
- **[library]** **pass one, reciprocal.** Draws the spine: from the current room, take an unused
  direction and an unused pool room, connect them two-way, repeat to `spine_length`, then connect to
  the other anchor
- **[library]** **pass one, continued.** Every pool room not drawn into the spine is attached two-way
  to a random spine room
- **[library]** **pass two, one-way.** Only when `fill` is set: every remaining unused direction on
  every **pool** room gets a one-way exit to a random **pool** room
- **[library]** tags every exit it creates, as it creates it

### Both draws are without replacement

The next room comes from the rooms not yet used, and the direction from that room's directions not yet
used. Drawing with replacement gives a spine that can revisit a room, connect a room to itself, or
wander without ever reaching the far anchor — a dungeon that is sometimes unsolvable, which is
indistinguishable from a bug.

### Pass one is reciprocal, pass two is one-way

The spine and the attachment of the leftover rooms are two-way, so a player can always walk back the
way they came and no room can be entered and not left. That satisfies the outbound-exit invariant by
construction rather than by a check.

Pass two is where the disorientation comes from: go west through the trees, come back east, and you
are somewhere else. One-way is also the simpler build — there is no matching return exit to invent.

### Pass two never touches an anchor, at either end

**Not as a target**, or a player guessing directions can be dumped at the far anchor and complete the
passage without ever finding the route. With a couple of spare directions across a dozen rooms that is
not a remote possibility, it is a regular occurrence.

**Not as a source**, or the anchor — an ordinary world room, at the edge of the forest — sprouts an
exit in every free compass direction, eating directions the consumer's world content may want.

So the anchors are touched exactly once each, by the spine, and never again.

### Filling is what makes it a wood rather than a corridor

One flag decides it, and it is the seam that lets one type serve both cases:

- **`fill` off.** Spare directions stay empty. The dungeon is a route with side branches — the
  leftover rooms hang off the spine as dead ends you explore out to and retrace.
- **`fill` on.** Every spare direction leads somewhere. The dungeon is disorienting: every direction
  is a plausible way forward and only one of them is.

### Deletion is the one dangerous operation

It deletes by the exit tag and by nothing else, so consumer-authored content survives — the anchors'
ways out into the wider world, and any exit someone wrote between two dungeon rooms in YAML.

It deletes objects one at a time. A queryset `.delete()` bypasses Evennia's `at_object_delete()`.

### Why the rooms are permanent

Because everything that goes wrong with a procedurally generated dungeon goes wrong when a room a
player is standing in stops existing.

The alternative — generating rooms on traversal and deleting them when the instance empties — was what
FCM ran, and it produced orphaned rooms after a crash, collapse racing against corpses, stale
references to rooms that had gone, and a boot-time sweep to clear up what was left. None of those are
layout problems. They are all lifecycle.

Permanent rooms remove the category. There is no instance to collapse, nothing to sweep, and a player
standing in a dungeon room when the rewire fires simply finds different exits.

The cost is that a dungeon is shared world space rather than a private instance: everyone in it sees
the same layout, and a solved route can be shared between players until the next cycle. That is
accepted — the cycle is what defeats memorisation, not secrecy.

## What the library does not do

**No settings.** Everything a type needs is in the object the consumer constructed or resolvable from
tags. There is consequently no boot check: validation happens at the start of a run, when the world
actually exists.

**No clock.** A type exposes the call; the consumer decides what triggers it. FCM drives it from
`evennia-calendar` signals, which handles per-dungeon cadence — one custom signal per cadence, a
receiver per dungeon. That is convenience, not a dependency: nothing here imports the calendar, and a
consumer wanting a flat real-time cycle writes a `LoopingCall` instead.

**No rooms.** `FixedRoomDungeon` never creates or deletes one. See above.

## What was surveyed and set aside

BSP, cellular automata, agent-based digging, rooms-and-mazes, Delaunay triangulation with a minimum
spanning tree, graph grammars, wave function collapse. All are tile-oriented or geometry-oriented, and
a MUD room is a graph node — there is no coordinate space here, so nothing can overlap and there is no
constraint for a generator to violate. That absence is why this algorithm is a few dozen lines rather
than a subsystem.

They are recorded here so the next session knows they were considered rather than missed.
