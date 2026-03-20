"""Number platform for Prolite Display."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .hub import ProliteHub

_LOGGER = logging.getLogger(__name__)


class ProliteNumberBase(NumberEntity):
    """Base class for Prolite number entities."""

    _attr_has_entity_name = True

    def __init__(self, hub: ProliteHub) -> None:
        """Initialize the base number entity."""
        self._hub = hub

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._hub.hub_id)},
            "name": self._hub.name,
            "manufacturer": self._hub.manufacturer,
            "model": self._hub.model,
        }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Prolite Display number entities."""
    hub: ProliteHub = entry.runtime_data

    entities = [
        ProliteSpeedNumber(hub),
    ]

    async_add_entities(entities)


class ProliteSpeedNumber(ProliteNumberBase):
    """Representation of a Prolite Display speed control."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 25
    _attr_native_step = 1

    def __init__(self, hub: ProliteHub) -> None:
        """Initialize the number entity."""
        super().__init__(hub)
        self._attr_unique_id = f"{hub.hub_id}_speed"
        self._attr_name = "Scroll Speed"
        self._attr_native_value = 12

    async def async_set_native_value(self, value: float) -> None:
        """Set the speed value."""
        self._attr_native_value = int(value)
        await self._hub.set_speed(int(value))
        self.async_write_ha_state()
