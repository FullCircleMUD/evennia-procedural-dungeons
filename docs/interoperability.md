# Interoperability

This library against every sibling library in `libraries/`, including itself. A reader deciding
whether two of our libraries can be co-installed gets a definite statement from either side rather
than inferring from silence.

Each section names the relationship — **hard dependency**, **optional integration**, **indirect
dependency** or **no coupling** — followed either by the constraints that apply or by an explicit
clearance stating *why* it is clear in terms of what this library does. "No known issues" is not a
clearance.

**The library has no behaviour yet**, so every statement below is provisional. The clearances rest on
four properties the agreed design holds: it owns no tables and stores nothing of its own; it reads no
settings; it owns no clock, so nothing it does happens unless a consumer asks; and it only ever
deletes what it created, identified by its own tag.

The library holds a type per kind of dungeon, and `FixedRoomDungeon` is the only one so far. Where a
statement below depends on that type's promises — chiefly that it creates and deletes exits and never
a room — it says so, because a later type is not bound by them.

## evennia-ai-memory

**No coupling.** Neither library imports the other. ai-memory stores what an NPC knows in its own
tables; this library writes exits. An NPC that remembers the way through a dungeon would be a consumer
feeding room names into its own prompt code, and the memory would go stale at the next rewire like any
other player's.

## evennia-archive

**No coupling.** Neither library imports the other. Archive clones Evennia's schema to preserve
characters across a world rebuild; this library's output is exits, which are regenerated from scratch
on every cycle and are worth nothing preserved. A character archived while standing in a dungeon room
comes back to whatever wiring exists then, which is the same thing that happens to a character who
logs out and back in.

## evennia-calendar

**No coupling, and deliberately so.** Neither library imports the other, and this library declares no
dependency on it.

This is the pairing a consumer is most likely to make. This library owns no clock — a type exposes the
call and nothing triggers it — and the calendar's custom signals are a good way to drive one, because
they solve per-dungeon cadence without this library having to schedule anything: register a signal
keyed on the condition you want, connect a receiver that calls `rewire()`.

Keeping it out of `pyproject.toml` is the point. A consumer who wants a flat real-time cycle writes a
`LoopingCall` and installs no calendar; one who wants game-time cadence has the calendar already. And
the condition — a game day, a season, every tenth day — is a game-design decision the library could
not write for them.

One trap, and it is the calendar's to document rather than ours: Django holds signal receivers weakly,
so a receiver that goes out of scope is collected and the dungeon silently stops rewiring. See
[custom-signals.md](../../evennia-calendar/docs/custom-signals.md) § holding on to your receiver.

## evennia-database-cascade

**No coupling.** Neither library imports the other. This library owns no models and declares no spec:
rooms and exits are Evennia objects and live in the game database by definition, so there is no alias
for a cascade to route.

## evennia-effects-conditions

**No coupling.** Neither library imports the other. Effects and conditions hang off actors; this
library wires rooms. A condition that disorients a player is the consumer's business and needs nothing
from the wiring underneath.

## evennia-environment

**No coupling.** Neither library imports the other. Environment describes what a room is like; this
library decides what leads out of it. Both write to rooms and neither reads the other's state — the
descriptions stay put across a rewire, which is the point of the rooms being permanent.

## evennia-equipment

**No coupling.** Neither library imports the other. Equipment is character state. Nothing this library
does is visible to it.

## evennia-llm-service

**No coupling.** Neither library imports the other. llm-service is a provider client and a template
loader; it holds no game objects and reads no exits.

## evennia-logging-extension

**Hard dependency.** `log.py` binds `dungeons_log` through its `make_logger`, and every line the
library emits goes through that binding to `dungeons.log`. The library does not run without it —
`pyproject.toml` declares it. Nothing flows the other way.

## evennia-message-bus

**No coupling.** Neither library imports the other. The bus carries messages between instances; this
library writes exits inside one. A deployment running both would need the rewire to happen once rather
than once per instance — that is the same constraint recorded under *evennia-scaling* below, and it is
that library's to own.

## evennia-mob-decision-engine

**No coupling.** Neither library imports the other. The decision engine reasons about what a mob does;
this library changes what the mob can walk through. A mob holding a remembered route across a rewire
would be walking a path that no longer exists, which is a consumer concern and the same one a player
has. `[TBD — needs discussion: whether the library should say anything to mobs mid-dungeon when the
wiring changes under them.]`

## evennia-mob-spawner

**No coupling.** Neither library imports the other. Spawn rules are keyed to rooms, and the rooms are
permanent — that is what makes the pairing safe. A spawn rule on a dungeon room keeps working across a
rewire because nothing it points at has gone.

## evennia-portal-multiplex

**No coupling.** Neither library imports the other. The multiplex is a connection-layer concern; this
library writes game objects and dispatches nothing off the reactor thread.

## evennia-procedural-dungeons

This library.

## evennia-scaling

**No coupling** in code — neither library imports the other — but the one real constraint in this
document lives here. The rewire is a whole-dungeon operation over shared world state, so a deployment
running more than one Evennia process needs it to happen exactly once rather than once per process.
Two processes rewiring the same dungeon would each delete the other's exits mid-pass.

`[TBD — needs discussion: which side owns that constraint. This library has no trigger yet, so there
is nothing to constrain until the rewire has something driving it.]`

## evennia-shards

**No coupling.** Neither library imports the other, and shards is being retired in favour of
`evennia-scaling` — the multi-process constraint is recorded there rather than here.

## evennia-survival

**No coupling.** Neither library imports the other. Survival meters are state on a holder; this
library writes exits. A player getting lost for longer gets hungrier, which is the two libraries doing
their own jobs rather than an interaction.

## evennia-targeting

**No coupling.** Neither library imports the other, and this library declares no targeting callables,
so it carries no `targeting.py`. If it ever needs a predicate, the standard's rule applies and the
file arrives with it.

## evennia-world-builder

**No coupling in code, and the closest pairing in practice.** Neither library imports the other.
world-builder authors the rooms and the tags that put them in a dungeon; this library reads those tags
and wires between them. The division is that every room and every tag is world-builder's output and
permanent, while every exit carrying `dungeon_exit` is this library's and transient. A consumer
authoring an exit between two dungeon rooms in YAML gets to keep it — it carries no `dungeon_exit`
tag, so the rewire never sees it.

## evennia-yaml-reader

**No coupling.** Neither library imports the other, and this library never reads a file. A consumer's
dungeon tags will most likely reach the world as YAML, but that is world-builder's path and this
library sees only the tags that arrive on the rooms.

## fcm-subscriptions

**No coupling.** Neither library imports the other. Subscriptions gate what an account may do; this
library writes exits and knows nothing about accounts.

## fcm-telemetry-spawn

**No coupling.** Neither library imports the other. Telemetry-spawn reads the economy and places
items; this library places exits. Both write to rooms and neither reads the other's writes.

## fcm-xrpl

**No coupling.** Neither library imports the other. xrpl mirrors ownership on-chain; this library
owns nothing ownable — an exit it made is deleted at the next cycle.
