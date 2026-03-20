"""Text platform for Prolite Display."""
from __future__ import annotations

import logging

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PAGES
from .hub import ProliteHub

_LOGGER = logging.getLogger(__name__)


class ProliteTextBase(TextEntity):
    """Base class for Prolite text entities."""

    _attr_has_entity_name = True

    def __init__(self, hub: ProliteHub) -> None:
        """Initialize the base text entity."""
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
    """Set up Prolite Display text entities."""
    hub: ProliteHub = entry.runtime_data

    entities = []
    for page in PAGES[:10]:
        entities.append(ProlitePageText(hub, page))

    async_add_entities(entities)


class ProlitePageText(ProliteTextBase):
    """Representation of a Prolite Display page text entity."""

    def __init__(self, hub: ProliteHub, page: str) -> None:
        """Initialize the text entity."""
        super().__init__(hub)
        self._page = page
        self._attr_unique_id = f"{hub.hub_id}_page_{page}_text"
        self._attr_name = f"Page {page} Text"
        self._attr_native_value = ""

    async def async_set_value(self, value: str) -> None:
        """Set the text value and send to display."""
        self._attr_native_value = value
        await self._hub.send_message(
            page=self._page,
            text=value,
        )
        self.async_write_ha_state()
