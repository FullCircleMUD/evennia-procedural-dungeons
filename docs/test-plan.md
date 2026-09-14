# Test plan

Every test case the library commits to covering, and the test function that covers it. The library is
built test-first: cases are agreed here, tests are written against them, then the implementation is
written to pass. The **Test function** column is the auditable trail — it is filled in as each test is
written, so an empty cell means the case is agreed but not yet covered.

Case IDs are stable and referenceable. Do not renumber; retire an ID rather than reuse it. Every test
function carries its case ID as its docstring, so the trail reads in both directions.

All test functions live in `src/evennia_procedural_dungeons/tests.py`.

Behaviour is agreed here first, before any test or code — see
[test-first-process.md](../../../design/test-first-process.md).

**This plan carries the scaffold case only.** `FixedRoomDungeon`'s cases have not been written yet —
that is the next piece of work, against the algorithm in [design.md](design.md). The prefixes below
are reserved so the IDs are stable when they land.

The library holds a type per kind of dungeon; a second type gets its own prefixes in this same plan.

| Prefix | Covers |
|---|---|
| `SC` | The scaffold — the library is installed and the runner reaches it |
| `EX` | The exit builders — the shared module-level helpers every dungeon type wires through |
| `DG` | `FixedRoomDungeon` the dataclass — its fields, and that it is frozen |
| `TG` | Tag resolution — finding a dungeon's pool rooms, its two anchors, and its exits, and refusing a set that cannot make a dungeon |
| `SP` | The spine — the route drawn between the anchors, and the without-replacement draws |
| `LO` | Leftover rooms — the pool rooms not drawn into the spine |
| `FI` | The fill pass — one-way exits on spare directions, and what it must not touch |
| `RW` | `rewire()` as a whole — delete, regenerate, and the invariants that hold afterwards |

## Fixtures

The fake objects the suite needs, named and purposed.

| Fixture | Purpose |
|---|---|
| `DIRECTIONS` | A `directions` mapping as a consumer would declare one — each direction to its opposite, symmetric. The four compass points plus `up`/`down`, so the `EX` cases have a direction whose opposite is not another compass point |
| `make_room` | Creates a room of the consumer's `BASE_ROOM_TYPECLASS`. Rooms are real Evennia objects rather than fakes: the helper sets `location` and `destination`, which only mean anything against the real thing |

## Cases

One section per function or surface, each with its own prefix and its own table.

### SC — the scaffold

Not behaviour of the library, but a check that there is a library to test. These fail when the editable
install is missing, when the test settings do not name the app, or when the runner cannot find the test
module — each of which otherwise looks like "no tests ran".

| ID | Case | Test function |
|---|---|---|
| SC-01 | The package is importable and carries its version | test_sc_01_the_package_is_importable_and_versioned |

### EX — the exit builders

Module-level helpers in `exits.py`, shared by every dungeon type. They are module-level rather than
methods so a second type can reuse them without inheriting from the first — and so they test against
two rooms and a direction, with no dungeon to construct.

A type's own method wraps the helper, and that method is the documented override point. **Library code
always goes through the method, never the helper directly** — otherwise a consumer's override applies
to part of a dungeon and not the rest. That is an `RW` case, not one of these.

`build_reciprocal_exits(room_a, room_b, direction, directions, dungeon_id, aliases=None)` builds one
exit and its reciprocal.

| ID | Case | Test function |
|---|---|---|
| EX-01 | Creates two exits — one in each room | test_ex_01_creates_one_exit_in_each_room |
| EX-02 | The forward exit's destination is room B; the return exit's is room A | test_ex_02_each_exit_leads_to_the_other_room |
| EX-03 | The forward exit is keyed by the direction given, not by the destination room's name | test_ex_03_the_forward_exit_is_keyed_by_direction_not_destination |
| EX-04 | The return exit is keyed by that direction's opposite, read from the `directions` mapping | test_ex_04_the_return_exit_is_keyed_by_the_mapped_opposite |
| EX-05 | Both exits are tagged with the dungeon id under the exit tag category, by the helper itself | test_ex_05_both_exits_are_tagged_with_the_dungeon_id |
| EX-06 | Both exits are created as `settings.BASE_EXIT_TYPECLASS` | test_ex_06_both_exits_use_the_configured_exit_typeclass |
| EX-07 | Returns both exits, forward first | test_ex_07_returns_both_exits_forward_first |
| EX-08 | A direction absent from the `directions` mapping is refused, and the message names it | test_ex_08_an_unmapped_direction_is_refused_and_named |
| EX-09 | Each exit carries the alias mapped to its own direction — the return exit takes the opposite's | test_ex_09_each_exit_carries_its_own_directions_alias |
| EX-10 | No `aliases` mapping means no aliases; the exits carry only their direction key | test_ex_10_without_a_mapping_the_exits_carry_no_aliases |
| EX-11 | A direction absent from the `aliases` mapping gets no alias, while the others still do | test_ex_11_a_direction_left_out_of_the_mapping_gets_no_alias |

**EX-03 is a deliberate departure** from how the first consumer builds exits today. Keying an exit
after its destination room hands a player the route: the one exit named differently from its
neighbours is the way on, and the dungeon is solved by reading rather than exploring.

**EX-05 puts the tagging in the helper rather than the caller.** Everything a type makes is tagged as
it is made. Tagging at the call site leaves a window where an exit exists untagged, and a path where
someone forgets — and the rewire can only delete what carries the tag.

**`aliases` is optional at both levels** — omit the mapping and no exit gets one; leave a direction out
of it and only that direction goes without. That is what makes `in`/`out` work without a rule: a
derivation would give them `i` and `o`, so a consumer simply leaves them out.

**Not covered here: two directions mapped to the same alias.** A room would end up with two exits
answering to it and Evennia would ask the player which they meant. The helper sees one direction per
call and cannot spot it, so it belongs with the `TG` checks.

## Open decisions

- `[TBD — needs discussion: FixedRoomDungeon's own cases. The algorithm is agreed in design.md;
  writing the cases against it is the next piece of work after the exit builders.]`
