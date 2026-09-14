# Installing

What a game has to do to run this library.

**Steps 1 and 2 exist today. Steps 3 to 5 describe the agreed shape and nothing implements them yet**
— installing the library right now gets you an importable package that does nothing. They are written
down because the shape is settled, not because it works; see [design.md](design.md).

## 1. Install the package

Nothing is published yet, so install from a checkout — and `evennia-logging-extension`, the one
dependency beyond Evennia itself, is also unpublished, so it installs from its own checkout first:

```
pip install -e path/to/evennia-logging-extension
pip install -e path/to/evennia-procedural-dungeons
```

## 2. Add the app

In your settings, below `from evennia.settings_default import *`:

```python
INSTALLED_APPS += ["evennia_procedural_dungeons"]
```

The import goes below the Evennia import because `LOG_DIR` is set by it, and the library's log binding
resolves the directory at import time.

## 3. Author and tag your rooms

Build the rooms however you build the rest of your world. Then tag them, all keyed by an id you choose
for this dungeon:

| Tag | On | How many |
|---|---|---|
| `dungeon_room: <id>` | every room the route may run through | as many as you like, at least `spine_length` |
| `dungeon_anchor: <id>` | the two fixed ends | exactly two |

An anchor must **not** also carry `dungeon_room` — it is an endpoint, never a room the route is drawn
through.

You do not tag exits. The library tags every exit it creates, with `dungeon_exit: <id>`, and deletes
by that tag and nothing else. An exit you authored yourself — an anchor's way out into the wider
world, or a shortcut between two dungeon rooms — carries no such tag and is never touched.

## 4. Construct the dungeon

```python
from evennia_procedural_dungeons.fixed_rooms import FixedRoomDungeon

deep_woods = FixedRoomDungeon(
    dungeon_id="deep_woods",
    spine_length=8,
    fill=True,
    directions=...,   # the compass this dungeon uses, with opposites
)
```

`fill=True` gives a disorienting wood: every spare direction leads somewhere, and only one of them
leads on. `fill=False` gives a route with dead-end side branches you explore out to and retrace.

## 5. Call `rewire()` on whatever schedule you want

```python
deep_woods.rewire()
```

The library owns no clock. Drive it from a `LoopingCall`, from a Django signal, from a command — it is
one call and it does not care what made it.

If you already run [`evennia-calendar`](../../evennia-calendar/docs/custom-signals.md), its custom
signals handle per-dungeon cadence neatly: register a signal keyed on the condition you want — a game
day, a season, every tenth day — and connect a receiver that calls `rewire()`. This library does not
depend on the calendar and never imports it; that is just a convenient thing to have lying around.

## Required settings

**None.** This library reads no settings and has none to read. Everything it needs is in the object
you constructed or resolvable from the tags on your rooms.

## Optional settings

**None**, for the same reason.

## What is not checked for you

- **`INSTALLED_APPS`.** Leave the library out of it and the app never registers. Nothing reports this:
  the package stays importable.
- **Your tags, until you call `rewire()`.** There is no boot check, because at boot the world may not
  be built. Validation happens at the start of a run — exactly two anchors, anchors disjoint from the
  pool, enough pool rooms for the spine — and a dungeon that fails refuses loudly rather than
  half-building something.
- **That your receiver stays alive**, if you drive this from Django signals. Django holds receivers
  weakly, so one that goes out of scope is silently collected and the dungeon simply stops rewiring —
  which looks exactly like this library being broken. The calendar documents the trap under
  [*holding on to your receiver*](../../evennia-calendar/docs/custom-signals.md).
