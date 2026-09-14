# SPDX-License-Identifier: BSD-3-Clause
"""The Django app.

``ready()`` is where the boot work will go — validating the consumer's
configuration, and starting whatever drives the rewire cycle. Neither exists
yet: what a consumer declares has not been decided. See docs/installing.md.
"""

from django.apps import AppConfig


class ProceduralDungeonsConfig(AppConfig):
    """The app registration. Nothing runs at boot yet."""

    name = "evennia_procedural_dungeons"
    label = "evennia_procedural_dungeons"
    verbose_name = "Evennia Procedural Dungeons"
