# SPDX-License-Identifier: BSD-3-Clause
"""The library's module-level constants, in the one place they are declared.

Every other module imports from here — see ``library-standards.md`` § Where
constants are declared.

The three tag categories below are ``FixedRoomDungeon``'s whole identification
surface. A dungeon is not an object the library stores; it is whatever carries
these tags with the same key. The key is the dungeon's id, chosen by the
consumer when they author the rooms — so adding a dungeon is one new id and no
new vocabulary.

**This library declares no settings of its own.** Everything a type needs is
either in the object the consumer constructed or resolvable from these tags.
It reads one of Evennia's — ``BASE_EXIT_TYPECLASS``, so the exits it builds
are the consumer's own kind — through the accessor below. A later type needing
its own categories declares them here too.
"""

#: Rooms the route is drawn through. Keyed by the dungeon id. These are the
#: only rooms the generator draws from, and the only rooms it wires spare
#: directions on.
TAG_CATEGORY_ROOM = "dungeon_room"

#: The two fixed rooms the route runs between. Keyed by the dungeon id, and
#: deliberately disjoint from the room tag: an anchor is an endpoint, never a
#: draw candidate. Which of the two the generator starts from does not matter.
TAG_CATEGORY_ANCHOR = "dungeon_anchor"

#: Every exit the library creates, keyed by the dungeon id. A type only ever
#: deletes what it created, so this is what makes a rewire safe: the anchors'
#: exits out to the wider world carry no such tag and survive, as does an exit
#: a consumer authored between two dungeon rooms.
TAG_CATEGORY_EXIT = "dungeon_exit"

#: Evennia's own setting, naming the exit typeclass the consumer's game uses.
#: Read rather than parameterised: a library exit should be the same kind of
#: thing as every other exit in the game it is installed in.
SETTING_EXIT_TYPECLASS = "BASE_EXIT_TYPECLASS"


def get_exit_typeclass() -> str:
    """Return the consumer's exit typeclass path.

    No fallback: ``BASE_EXIT_TYPECLASS`` is set by Evennia's own
    ``settings_default``, so there is no undeclared case to protect against.
    The accessor exists to defer the read and to keep the setting name in one
    place.
    """
    from django.conf import settings

    return settings.BASE_EXIT_TYPECLASS
