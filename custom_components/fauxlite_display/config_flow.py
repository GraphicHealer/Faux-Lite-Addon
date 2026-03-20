"""Config flow for Prolite Display integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout
import voluptuous as vol
from zeroconf import ServiceStateChange, Zeroconf
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_SIGN_ID,
    DEFAULT_SIGN_ID,
)
from .hub import ProliteHub

_LOGGER = logging.getLogger(__name__)

SCAN_TIMEOUT = 5


async def discover_faux_lite_devices(hass: HomeAssistant) -> list[dict[str, str]]:
    """Discover Faux-Lite devices on the network using mDNS."""
    devices = []

    try:
        aiozc = await zeroconf.async_get_async_instance(hass)

        class FauxLiteListener:
            """Listener for Faux-Lite mDNS services."""

            def __init__(self):
                self.devices = []

            def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                """Handle service added."""
                asyncio.create_task(self._async_add_service(zc, type_, name))

            async def _async_add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                """Async handler for service added."""
                try:
                    info = AsyncServiceInfo(type_, name)
                    await info.async_request(zc, 3000)

                    if info and info.addresses:
                        # Get first IPv4 address
                        for addr in info.addresses:
                            ip = ".".join(str(b) for b in addr)

                            # Verify it's a Faux-Lite device
                            session = async_get_clientsession(hass)
                            try:
                                async with async_timeout.timeout(3):
                                    async with session.get(f"http://{ip}/api/info") as response:
                                        if response.status == 200:
                                            data = await response.json()
                                            if data.get("device") == "faux-lite":
                                                device_info = {
                                                    "host": ip,
                                                    "name": f"Faux-Lite {data.get('chip_id', 'Unknown')}",
                                                    "chip_id": data.get("chip_id", "Unknown"),
                                                    "sign_id": data.get("sign_id", DEFAULT_SIGN_ID),
                                                }
                                                if device_info not in self.devices:
                                                    self.devices.append(device_info)
                                                    _LOGGER.info("Discovered Faux-Lite: %s at %s", device_info["name"], ip)
                                                break
                            except Exception as err:
                                _LOGGER.debug("Error verifying device at %s: %s", ip, err)
                except Exception as err:
                    _LOGGER.debug("Error processing mDNS service %s: %s", name, err)

            def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                """Handle service updated."""
                pass

            def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
                """Handle service removed."""
                pass

        listener = FauxLiteListener()
        browser = AsyncServiceBrowser(aiozc.zeroconf, ["_http._tcp.local."], listener)

        # Wait for discovery
        await asyncio.sleep(SCAN_TIMEOUT)

        await browser.async_cancel()
        devices = listener.devices

    except Exception as err:
        _LOGGER.error("Error during mDNS discovery: %s", err)

    return devices


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    hub = ProliteHub(hass, data)

    if not await hub.async_setup():
        raise CannotConnect

    if not await hub.test_connection():
        await hub.close()
        raise CannotConnect

    # Get device info for title
    info = await hub.get_sign_info()
    await hub.close()

    chip_id = info.get("chip_id", "Unknown") if info else "Unknown"
    return {"title": f"Faux-Lite {chip_id}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Prolite Display."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._discovered_devices = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - immediately scan for devices."""
        return await self.async_step_scan(user_input)

    async def async_step_scan(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device discovery via mDNS."""
        if user_input is not None:
            # User selected a device or chose manual entry
            if user_input.get("device") == "manual":
                return await self.async_step_manual()

            # Find the selected device
            selected_host = user_input["device"]
            selected_device = next(
                (d for d in self._discovered_devices if d["host"] == selected_host),
                None
            )

            if selected_device:
                data = {
                    CONF_HOST: selected_device["host"],
                    CONF_SIGN_ID: selected_device["sign_id"],
                }

                try:
                    info = await validate_input(self.hass, data)

                    await self.async_set_unique_id(f"faux_lite_{selected_device['chip_id']}")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(title=info["title"], data=data)
                except CannotConnect:
                    return self.async_abort(reason="cannot_connect")
                except Exception:
                    _LOGGER.exception("Unexpected exception")
                    return self.async_abort(reason="unknown")

        # Scan for devices
        _LOGGER.info("Scanning for Faux-Lite devices...")
        self._discovered_devices = await discover_faux_lite_devices(self.hass)

        # Build device selection list (always include manual entry option)
        device_options = [
            {"label": f"{d['name']} ({d['host']})", "value": d["host"]}
            for d in self._discovered_devices
        ]
        device_options.append({"label": "Add device manually", "value": "manual"})

        data_schema = vol.Schema({
            vol.Required("device"): vol.In({d["value"]: d["label"] for d in device_options}),
        })

        description = (
            f"Found {len(self._discovered_devices)} device(s)"
            if self._discovered_devices
            else "No devices found. You can add a device manually."
        )

        return self.async_show_form(
            step_id="scan",
            data_schema=data_schema,
            description_placeholders={
                "count": str(len(self._discovered_devices)),
                "description": description
            },
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual IP entry."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                # Get device info for unique ID
                hub = ProliteHub(self.hass, user_input)
                await hub.async_setup()
                device_info = await hub.get_sign_info()
                await hub.close()

                chip_id = device_info.get("chip_id", user_input[CONF_HOST].replace(".", "_")) if device_info else user_input[CONF_HOST].replace(".", "_")

                await self.async_set_unique_id(f"faux_lite_{chip_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_SIGN_ID, default=DEFAULT_SIGN_ID): str,
        })

        return self.async_show_form(
            step_id="manual", data_schema=data_schema, errors=errors
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
