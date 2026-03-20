"""The Prolite Display integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN
from .hub import ProliteHub

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.TEXT, Platform.SELECT, Platform.NUMBER]

type ProliteConfigEntry = ConfigEntry[ProliteHub]


async def async_setup_entry(hass: HomeAssistant, entry: ProliteConfigEntry) -> bool:
    """Set up Prolite Display from a config entry."""
    hub = ProliteHub(hass, entry.data)

    if not await hub.async_setup():
        return False

    entry.runtime_data = hub

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def async_set_message(call):
        """Handle the set_message service call."""
        await hub.send_message(
            page=call.data.get("page", "A"),
            text=call.data["text"],
            color=call.data.get("color"),
            font=call.data.get("font"),
            size=call.data.get("size"),
            function=call.data.get("function"),
            beep=call.data.get("beep", False),
        )

    async def async_send_message(call):
        """Handle the send_message service call (one-shot message)."""
        await hub.send_oneshot_message(
            text=call.data["text"],
            color=call.data.get("color"),
            font=call.data.get("font"),
            size=call.data.get("size"),
            function=call.data.get("function"),
            exit_function=call.data.get("exit_function"),
            beep=call.data.get("beep", False),
            repeat=call.data.get("repeat", 1),
        )

    async def async_delete_page(call):
        """Handle the delete_page service call."""
        await hub.delete_page(call.data.get("page", "*"))

    async def async_run_page(call):
        """Handle the run_page service call."""
        await hub.run_page(call.data["page"])

    async def async_set_speed(call):
        """Handle the set_speed service call."""
        await hub.set_speed(call.data["speed"])

    async def async_set_time(call):
        """Handle the set_time service call."""
        await hub.set_time()

    async def async_create_graphic(call):
        """Handle the create_graphic service call."""
        await hub.create_graphic(
            block=call.data["block"],
            pattern=call.data["pattern"]
        )

    async def async_send_formatted_message(call):
        """Handle the send_formatted_message service call."""
        await hub.send_formatted_message(
            page=call.data.get("page", "A"),
            segments=call.data["segments"],
            function=call.data.get("function"),
        )

    async def async_send_raw_protocol(call):
        """Handle the send_raw_protocol service call."""
        await hub.send_raw_protocol(
            page=call.data.get("page", "A"),
            protocol_string=call.data["protocol_string"],
        )

    async def async_send_beep(call):
        """Handle the send_beep service call."""
        await hub.send_beep(
            count=call.data.get("count", 1),
        )

    async def async_show_time(call):
        """Handle the show_time service call."""
        await hub.show_time(
            page=call.data.get("page", "A"),
        )

    async def async_show_date(call):
        """Handle the show_date service call."""
        await hub.show_date(
            page=call.data.get("page", "A"),
        )

    async def async_pause_display(call):
        """Handle the pause_display service call."""
        await hub.pause_display(
            page=call.data.get("page", "A"),
        )

    async def async_show_thank_you(call):
        """Handle the show_thank_you service call."""
        await hub.show_thank_you(
            page=call.data.get("page", "A"),
        )

    async def async_show_welcome(call):
        """Handle the show_welcome service call."""
        await hub.show_welcome(
            page=call.data.get("page", "A"),
        )

    async def async_delete_graphic(call):
        """Handle the delete_graphic service call."""
        await hub.delete_graphic(call.data.get("block", "*"))

    async def async_delete_all(call):
        """Handle the delete_all service call."""
        await hub.delete_all()

    async def async_run_page_timed(call):
        """Handle the run_page_timed service call."""
        await hub.run_page_timed(
            page=call.data["page"],
            times=call.data["times"],
            next_page=call.data["next_page"],
        )

    async def async_count_up(call):
        """Handle the count_up service call."""
        await hub.count_up(
            unit=call.data["unit"],
            start_value=call.data["start_value"],
            target_value=call.data["target_value"],
            target_page=call.data["target_page"],
        )

    async def async_count_down(call):
        """Handle the count_down service call."""
        await hub.count_down(
            days=call.data.get("days", 0),
            hours=call.data.get("hours", 0),
            minutes=call.data.get("minutes", 0),
            target_page=call.data["target_page"],
        )

    async def async_get_sign_info(call):
        """Handle the get_sign_info service call."""
        await hub.get_sign_info()

    hass.services.async_register(DOMAIN, "set_message", async_set_message)
    hass.services.async_register(DOMAIN, "send_message", async_send_message)
    hass.services.async_register(DOMAIN, "send_formatted_message", async_send_formatted_message)
    hass.services.async_register(DOMAIN, "send_raw_protocol", async_send_raw_protocol)
    hass.services.async_register(DOMAIN, "send_beep", async_send_beep)
    hass.services.async_register(DOMAIN, "show_time", async_show_time)
    hass.services.async_register(DOMAIN, "show_date", async_show_date)
    hass.services.async_register(DOMAIN, "pause_display", async_pause_display)
    hass.services.async_register(DOMAIN, "show_thank_you", async_show_thank_you)
    hass.services.async_register(DOMAIN, "show_welcome", async_show_welcome)
    hass.services.async_register(DOMAIN, "delete_page", async_delete_page)
    hass.services.async_register(DOMAIN, "delete_graphic", async_delete_graphic)
    hass.services.async_register(DOMAIN, "delete_all", async_delete_all)
    hass.services.async_register(DOMAIN, "run_page", async_run_page)
    hass.services.async_register(DOMAIN, "run_page_timed", async_run_page_timed)
    hass.services.async_register(DOMAIN, "set_speed", async_set_speed)
    hass.services.async_register(DOMAIN, "set_time", async_set_time)
    hass.services.async_register(DOMAIN, "create_graphic", async_create_graphic)
    hass.services.async_register(DOMAIN, "count_up", async_count_up)
    hass.services.async_register(DOMAIN, "count_down", async_count_down)
    hass.services.async_register(DOMAIN, "get_sign_info", async_get_sign_info)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.services.async_remove(DOMAIN, "set_message")
        hass.services.async_remove(DOMAIN, "send_message")
        hass.services.async_remove(DOMAIN, "send_formatted_message")
        hass.services.async_remove(DOMAIN, "send_raw_protocol")
        hass.services.async_remove(DOMAIN, "delete_page")
        hass.services.async_remove(DOMAIN, "delete_graphic")
        hass.services.async_remove(DOMAIN, "delete_all")
        hass.services.async_remove(DOMAIN, "run_page")
        hass.services.async_remove(DOMAIN, "run_page_timed")
        hass.services.async_remove(DOMAIN, "set_speed")
        hass.services.async_remove(DOMAIN, "set_time")
        hass.services.async_remove(DOMAIN, "create_graphic")
        hass.services.async_remove(DOMAIN, "count_up")
        hass.services.async_remove(DOMAIN, "count_down")
        hass.services.async_remove(DOMAIN, "get_sign_info")

    return unload_ok
