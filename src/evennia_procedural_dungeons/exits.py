# SPDX-License-Identifier: BSD-3-Clause
"""The exit builders — shared machinery every dungeon type wires through.

Module-level rather than methods on a type, for two reasons. A second type
reuses them by importing rather than by inheriting, so the library shares code
without a base class extracted from a single implementation. And they test
against two rooms and a direction, with no dungeon to construct.

A type's own method wraps the helper, and that method is the documented
override point for a consumer whose exit typeclass needs more than the core
fields. **Library code always goes through the method, never the helper
directly** — otherwise an override applies to part of a dungeon and not the
rest, with nothing to say why.
"""

from .config import TAG_CATEGORY_EXIT, get_exit_typeclass


def build_reciprocal_exits(
    room_a, room_b, direction, directions, dungeon_id, aliases=None
):
    """Build an exit from A to B and its reciprocal from B to A.

    Both exits are keyed by the direction they lead in — never by the
    destination room's name, which would hand a player the route.

    Both are tagged here rather than by the caller. Everything a type makes is
    tagged as it is made: tagging at the call site leaves a window where an
    exit exists untagged, and a rewire can only delete what carries the tag.

    Args:
        room_a: The room the forward exit is placed in.
        room_b: The room it leads to, and where the return exit is placed.
        direction: The direction from A to B. Its opposite is read from
            ``directions``.
        directions: Mapping of direction to opposite, as the consumer
            declared it.
        dungeon_id: The tag key both exits carry, under
            ``TAG_CATEGORY_EXIT``.
        aliases: Optional mapping of direction to its short form. Omit it and
            no exit gets an alias; leave a direction out of it and only that
            direction goes without. That is what lets ``in``/``out`` work — a
            derivation would give them ``i`` and ``o``, so a consumer leaves
            them out instead.

    Returns:
        (exit_ab, exit_ba): The two exits, forward first.

    Raises:
        ValueError: ``direction`` is not in ``directions``, so there is no
            opposite to build the return exit in.
    """
    if direction not in directions:
        raise ValueError(
            f"{direction!r} is not in this dungeon's directions, so there is "
            f"no opposite to build the return exit in. Declared directions: "
            f"{', '.join(sorted(directions))}."
        )

    opposite = directions[direction]
    aliases = aliases or {}

    return (
        _build_exit(room_a, direction, room_b, dungeon_id, aliases.get(direction)),
        _build_exit(room_b, opposite, room_a, dungeon_id, aliases.get(opposite)),
    )


def _build_exit(room, direction, destination, dungeon_id, alias=None):
    """Build one exit and tag it, in that order.

    Tagging immediately after creation rather than once both exits exist: a
    failure building the second would otherwise leave an untagged first, which
    no rewire can find and no rewire can delete.

    ``alias`` is this exit's own short form, already looked up — each exit
    takes the alias for the direction it leads in, so the return exit gets the
    opposite's rather than the forward direction's.
    """
    # An exit is an Evennia object with a destination, so building one means
    # reaching for the engine's creator rather than constructing anything of
    # our own. Deferred to call time: this module is imported while Django is
    # still building its app registry.
    from evennia.utils.create import create_object

    exit_obj = create_object(
        get_exit_typeclass(),
        key=direction,
        aliases=[alias] if alias else None,
        location=room,
        destination=destination,
    )
    exit_obj.tags.add(dungeon_id, category=TAG_CATEGORY_EXIT)
    return exit_obj
