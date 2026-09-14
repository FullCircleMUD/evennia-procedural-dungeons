# SPDX-License-Identifier: BSD-3-Clause
"""Unit tests for evennia-procedural-dungeons. Run via ``python runtests.py``.

Each test's docstring is the case ID it covers, from docs/test-plan.md. The
plan is where behaviour is agreed; a test here without a case there is a test
nobody committed to.
"""

from unittest import TestCase as PlainTestCase

from django.conf import settings
from django.test import TestCase

import evennia_procedural_dungeons
from evennia_procedural_dungeons.config import TAG_CATEGORY_EXIT
from evennia_procedural_dungeons.exits import (
    build_oneway_exit,
    build_reciprocal_exits,
)

#: A ``directions`` mapping as a consumer would declare one. Symmetric, and
#: carrying a pair whose opposite is not another compass point, so a case can
#: show the opposite is read rather than guessed at.
DIRECTIONS = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
    "up": "down",
    "down": "up",
}

#: Short forms for the directions above, as a consumer would declare them.
#: Separate from ``DIRECTIONS`` because it is optional — a consumer who wants
#: players to type the whole word passes nothing.
ALIASES = {
    "north": "n",
    "south": "s",
    "east": "e",
    "west": "w",
    "up": "u",
    "down": "d",
}

DUNGEON_ID = "deep_woods"


def make_room(key):
    """Create a room of the consumer's own room typeclass.

    Real Evennia objects rather than fakes: the helper sets ``location`` and
    ``destination``, which only mean anything against the real thing.
    """
    # The builders work on live objects, so the suite needs the engine to make
    # them. Deferred to call time — importing Evennia at module scope would
    # run while the app registry is still being built.
    from evennia.utils.create import create_object

    return create_object(settings.BASE_ROOM_TYPECLASS, key=key)


class ScaffoldTests(PlainTestCase):
    """SC — the library is installed and the runner reaches it."""

    def test_sc_01_the_package_is_importable_and_versioned(self):
        """SC-01"""
        self.assertEqual(evennia_procedural_dungeons.__version__, "0.0.1")


class BuildReciprocalExitsTests(TestCase):
    """EX — ``build_reciprocal_exits``, the two-way builder."""

    def setUp(self):
        self.room_a = make_room("Room A")
        self.room_b = make_room("Room B")

    def build(self, direction="north", aliases=None):
        """Build a reciprocal pair between the two rooms."""
        return build_reciprocal_exits(
            self.room_a, self.room_b, direction, DIRECTIONS, DUNGEON_ID, aliases
        )

    def test_ex_01_creates_one_exit_in_each_room(self):
        """EX-01"""
        self.build()

        self.assertEqual(len(self.room_a.exits), 1)
        self.assertEqual(len(self.room_b.exits), 1)

    def test_ex_02_each_exit_leads_to_the_other_room(self):
        """EX-02"""
        exit_ab, exit_ba = self.build()

        self.assertEqual(exit_ab.destination, self.room_b)
        self.assertEqual(exit_ba.destination, self.room_a)

    def test_ex_03_the_forward_exit_is_keyed_by_direction_not_destination(self):
        """EX-03"""
        exit_ab, _ = self.build(direction="east")

        self.assertEqual(exit_ab.key, "east")
        self.assertNotEqual(exit_ab.key, self.room_b.key)

    def test_ex_04_the_return_exit_is_keyed_by_the_mapped_opposite(self):
        """EX-04"""
        _, exit_ba = self.build(direction="up")

        self.assertEqual(exit_ba.key, DIRECTIONS["up"])

    def test_ex_05_both_exits_are_tagged_with_the_dungeon_id(self):
        """EX-05"""
        exit_ab, exit_ba = self.build()

        self.assertTrue(exit_ab.tags.has(DUNGEON_ID, category=TAG_CATEGORY_EXIT))
        self.assertTrue(exit_ba.tags.has(DUNGEON_ID, category=TAG_CATEGORY_EXIT))

    def test_ex_06_both_exits_use_the_configured_exit_typeclass(self):
        """EX-06"""
        exit_ab, exit_ba = self.build()

        self.assertEqual(exit_ab.typeclass_path, settings.BASE_EXIT_TYPECLASS)
        self.assertEqual(exit_ba.typeclass_path, settings.BASE_EXIT_TYPECLASS)

    def test_ex_07_returns_both_exits_forward_first(self):
        """EX-07"""
        exit_ab, exit_ba = self.build()

        self.assertEqual(exit_ab.location, self.room_a)
        self.assertEqual(exit_ba.location, self.room_b)

    def test_ex_08_an_unmapped_direction_is_refused_and_named(self):
        """EX-08"""
        with self.assertRaises(ValueError) as raised:
            self.build(direction="widdershins")

        self.assertIn("widdershins", str(raised.exception))

    def test_ex_09_each_exit_carries_its_own_directions_alias(self):
        """EX-09"""
        exit_ab, exit_ba = self.build(direction="north", aliases=ALIASES)

        self.assertEqual(exit_ab.aliases.all(), ["n"])
        self.assertEqual(exit_ba.aliases.all(), ["s"])

    def test_ex_10_without_a_mapping_the_exits_carry_no_aliases(self):
        """EX-10"""
        exit_ab, exit_ba = self.build(direction="north")

        self.assertEqual(exit_ab.aliases.all(), [])
        self.assertEqual(exit_ba.aliases.all(), [])

    def test_ex_11_a_direction_left_out_of_the_mapping_gets_no_alias(self):
        """EX-11"""
        exit_ab, exit_ba = self.build(direction="north", aliases={"north": "n"})

        self.assertEqual(exit_ab.aliases.all(), ["n"])
        self.assertEqual(exit_ba.aliases.all(), [])


class BuildOnewayExitTests(TestCase):
    """EX — ``build_oneway_exit``, the builder the fill pass is made of."""

    def setUp(self):
        self.room_a = make_room("Room A")
        self.room_b = make_room("Room B")

    def build(self, direction="north", aliases=None):
        """Build a single exit from A to B."""
        return build_oneway_exit(
            self.room_a, direction, self.room_b, DIRECTIONS, DUNGEON_ID, aliases
        )

    def test_ex_12_creates_one_exit_and_no_return(self):
        """EX-12"""
        self.build()

        self.assertEqual(len(self.room_a.exits), 1)
        self.assertEqual(len(self.room_b.exits), 0)

    def test_ex_13_the_exit_leads_to_the_destination_given(self):
        """EX-13"""
        exit_obj = self.build()

        self.assertEqual(exit_obj.location, self.room_a)
        self.assertEqual(exit_obj.destination, self.room_b)

    def test_ex_14_the_exit_is_keyed_by_direction_not_destination(self):
        """EX-14"""
        exit_obj = self.build(direction="east")

        self.assertEqual(exit_obj.key, "east")
        self.assertNotEqual(exit_obj.key, self.room_b.key)

    def test_ex_15_the_exit_is_tagged_with_the_dungeon_id(self):
        """EX-15"""
        exit_obj = self.build()

        self.assertTrue(exit_obj.tags.has(DUNGEON_ID, category=TAG_CATEGORY_EXIT))

    def test_ex_16_the_exit_uses_the_configured_exit_typeclass(self):
        """EX-16"""
        exit_obj = self.build()

        self.assertEqual(exit_obj.typeclass_path, settings.BASE_EXIT_TYPECLASS)

    def test_ex_17_the_exit_carries_the_alias_for_its_direction(self):
        """EX-17"""
        exit_obj = self.build(direction="west", aliases=ALIASES)

        self.assertEqual(exit_obj.aliases.all(), ["w"])

    def test_ex_18_without_a_mapping_the_exit_carries_no_alias(self):
        """EX-18"""
        exit_obj = self.build()

        self.assertEqual(exit_obj.aliases.all(), [])

    def test_ex_19_an_unmapped_direction_is_refused_and_named(self):
        """EX-19"""
        with self.assertRaises(ValueError) as raised:
            self.build(direction="widdershins")

        self.assertIn("widdershins", str(raised.exception))
