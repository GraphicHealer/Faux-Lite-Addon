"""Select platform for Prolite Display."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, COLORS, FONTS, FUNCTIONS, PAGES
from .hub import ProliteHub

_LOGGER = logging.getLogger(__name__)


class ProliteSelectBase(SelectEntity):
    """Base class for Prolite select entities."""

    _attr_has_entity_name = True

    def __init__(self, hub: ProliteHub) -> None:
        """Initialize the base select entity."""
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
    """Set up Prolite Display select entities."""
    hub: ProliteHub = entry.runtime_data

    entities = [
        ProliteColorSelect(hub),
        ProliteFontSelect(hub),
        ProliteFunctionSelect(hub),
        ProliteActivePageSelect(hub),
    ]

    async_add_entities(entities)


class ProliteColorSelect(ProliteSelectBase):
    """Representation of a Prolite Display color selector."""

    def __init__(self, hub: ProliteHub) -> None:
        """Initialize the select entity."""
        super().__init__(hub)
        self._attr_unique_id = f"{hub.hub_id}_color"
        self._attr_name = "Color"
        self._attr_options = list(COLORS.keys())
        self._attr_current_option = "rainbow"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
        self.async_write_ha_state()


class ProliteFontSelect(ProliteSelectBase):
    """Representation of a Prolite Display font selector."""

    def __init__(self, hub: ProliteHub) -> None:
        """Initialize the select entity."""
        super().__init__(hub)
        self._attr_unique_id = f"{hub.hub_id}_font"
        self._attr_name = "Font"
        self._attr_options = list(FONTS.keys())
        self._attr_current_option = "normal"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
        self.async_write_ha_state()


class ProliteFunctionSelect(ProliteSelectBase):
    """Representation of a Prolite Display function selector."""

    def __init__(self, hub: ProliteHub) -> None:
        """Initialize the select entity."""
        super().__init__(hub)
        self._attr_unique_id = f"{hub.hub_id}_function"
        self._attr_name = "Function"
        self._attr_options = list(FUNCTIONS.keys())
        self._attr_current_option = "shift_left"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
        self.async_write_ha_state()


class ProliteActivePageSelect(ProliteSelectBase):
    """Representation of a Prolite Display active page selector."""

    def __init__(self, hub: ProliteHub) -> None:
        """Initialize the select entity."""
        super().__init__(hub)
        self._attr_unique_id = f"{hub.hub_id}_active_page"
        self._attr_name = "Active Page"
        self._attr_options = PAGES
        self._attr_current_option = "A"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option and run the page."""
        self._attr_current_option = option
        await self._hub.run_page(option)
        self.async_write_ha_state()
