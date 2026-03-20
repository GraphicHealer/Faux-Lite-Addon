"""Prolite Display Hub for HTTP communication with Faux-Lite."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_HOST,
    CONF_SIGN_ID,
    DEFAULT_SIGN_ID,
    DEFAULT_PORT,
    COLORS,
    FONTS,
    SIZES,
    FUNCTIONS,
)

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10


class ProliteHub:
    """Prolite Display Hub for managing HTTP communication with Faux-Lite."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize the Prolite hub."""
        self._hass = hass
        self._host = config.get(CONF_HOST)
        self._port = config.get("port", DEFAULT_PORT)
        self._sign_id = config.get(CONF_SIGN_ID, DEFAULT_SIGN_ID)
        self._lock = asyncio.Lock()
        self._session = async_get_clientsession(hass)
        self.manufacturer = "Faux-Lite"
        self.model = "WiFi-to-Serial Bridge"
        self.name = f"Faux-Lite Display {self._sign_id}"
        self._base_url = f"http://{self._host}:{self._port}"

    @property
    def hub_id(self) -> str:
        """Return the hub ID."""
        return f"prolite_{self._sign_id}"

    async def async_setup(self) -> bool:
        """Set up the Faux-Lite connection."""
        try:
            # Verify Faux-Lite device is accessible
            async with async_timeout.timeout(TIMEOUT):
                async with self._session.get(f"{self._base_url}/api/info") as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.info(
                            "Connected to Faux-Lite device: %s (Sign ID: %s)",
                            data.get("chip_id"),
                            data.get("sign_id")
                        )
                        return True
                    else:
                        _LOGGER.error("Failed to connect to Faux-Lite: HTTP %s", response.status)
                        return False
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout connecting to Faux-Lite at %s", self._base_url)
            return False
        except Exception as err:
            _LOGGER.error("Failed to connect to Faux-Lite: %s", err)
            return False

    async def _send_command(self, command: str) -> bool:
        """Send a command to the display via Faux-Lite REST API."""
        async with self._lock:
            try:
                _LOGGER.debug("Sending command to Faux-Lite: %s", command)

                # Send command via REST API
                async with async_timeout.timeout(TIMEOUT):
                    async with self._session.post(
                        f"{self._base_url}/api/send",
                        json={"command": command},
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            _LOGGER.debug("Command sent successfully to Faux-Lite")
                            return True
                        else:
                            _LOGGER.error("Failed to send command: HTTP %s", response.status)
                            return False

            except asyncio.TimeoutError:
                _LOGGER.error("Timeout sending command to Faux-Lite")
                return False
            except Exception as err:
                _LOGGER.error("Error sending command to Faux-Lite: %s", err)
                return False

    async def send_message(
        self,
        page: str,
        text: str,
        color: str | None = None,
        font: str | None = None,
        size: str | None = None,
        function: str | None = None,
        beep: bool = False,
    ) -> bool:
        """Send a message to a specific page."""
        _LOGGER.info(
            "send_message called with: page=%s, text=%s, color=%s, font=%s, size=%s, function=%s, beep=%s",
            page, text, color, font, size, function, beep
        )
        message_parts = [f"<P{page}>"]

        if function:
            func_code = FUNCTIONS.get(function, function)
            message_parts.append(f"<{func_code}>")
            _LOGGER.debug("Adding function: %s -> %s", function, func_code)

        if color:
            color_code = COLORS.get(color, color)
            message_parts.append(f"<{color_code}>")
            _LOGGER.debug("Adding color: %s -> %s", color, color_code)

        if font:
            font_code = FONTS.get(font, font)
            message_parts.append(f"<{font_code}>")
            _LOGGER.debug("Adding font: %s -> %s", font, font_code)

        if size:
            size_code = SIZES.get(size, size)
            message_parts.append(f"<{size_code}>")
            _LOGGER.debug("Adding size: %s -> %s", size, size_code)

        # Add beep if requested
        if beep:
            message_parts.append("<FB>")
            _LOGGER.debug("Adding beep command")

        # Add text as-is (no automatic trailing space)
        # Users can add trailing space manually if needed for looping
        message_parts.append(text)

        command = "".join(message_parts)
        _LOGGER.info("Constructed message command: %s", command)

        return await self._send_command(command)

    async def send_oneshot_message(
        self,
        text: str,
        color: str | None = None,
        font: str | None = None,
        size: str | None = None,
        function: str | None = None,
        exit_function: str | None = None,
        beep: bool = False,
        repeat: int = 1,
    ) -> bool:
        """Send a one-shot message that displays then clears (uses pages Z and Y).

        Args:
            text: Message text to display
            color: Color code (optional)
            font: Font code (optional)
            size: Size code (optional)
            function: Display function for the message (optional)
            exit_function: Function to use on page Y after message completes (optional, defaults to same as function)
            repeat: Number of times to display the message
        """
        _LOGGER.info(
            "send_oneshot_message called with: text=%s, color=%s, font=%s, size=%s, function=%s, exit_function=%s, beep=%s, repeat=%d",
            text, color, font, size, function, exit_function, beep, repeat
        )

        # Determine the function to use for page Y (exit/return page)
        # If exit_function is specified, use it; otherwise use the same function as the message
        y_function = exit_function if exit_function is not None else function

        # Step 1: Set page Y to blank with the exit function
        # Use single space to prevent demo mode
        await self.send_message(page="Y", text=" ", function=y_function)

        # Step 2: Set page Z with the message
        await self.send_message(
            page="Z",
            text=text,
            color=color,
            font=font,
            size=size,
            function=function,
            beep=beep,
        )

        # Step 3: Run page Z for 'repeat' times, then switch to blank page Y
        command = f"<RPZ><{repeat:02d}><RPY>"
        return await self._send_command(command)

    async def send_beep(self, count: int = 1) -> bool:
        """Send beep command to the display.

        Args:
            count: Number of beeps (1-99)
        """
        _LOGGER.info("send_beep called with: count=%d", count)

        # Beep command format: <FB> for single beep, or repeat on a page
        # For multiple beeps, we'll send the beep command multiple times
        if count < 1:
            count = 1
        if count > 99:
            count = 99

        # Use page Z for beep, then return to page A
        await self.send_message(page="Z", text=" ", beep=True)
        command = f"<RPZ><{count:02d}><RPA>"
        return await self._send_command(command)

    async def show_time(self, page: str = "A") -> bool:
        """Display current time on the sign.

        Args:
            page: Page to display time on
        """
        _LOGGER.info("show_time called with: page=%s", page)
        command = f"<P{page}><FT>"
        return await self._send_command(command)

    async def show_date(self, page: str = "A") -> bool:
        """Display current date on the sign.

        Args:
            page: Page to display date on
        """
        _LOGGER.info("show_date called with: page=%s", page)
        command = f"<P{page}><FD>"
        return await self._send_command(command)

    async def pause_display(self, page: str = "A") -> bool:
        """Pause the current display.

        Args:
            page: Page to apply pause to
        """
        _LOGGER.info("pause_display called with: page=%s", page)
        command = f"<P{page}><FP>"
        return await self._send_command(command)

    async def show_thank_you(self, page: str = "A") -> bool:
        """Display THANK YOU graphic.

        Args:
            page: Page to display graphic on
        """
        _LOGGER.info("show_thank_you called with: page=%s", page)
        command = f"<P{page}><FU>"
        return await self._send_command(command)

    async def show_welcome(self, page: str = "A") -> bool:
        """Display WELCOME graphic.

        Args:
            page: Page to display graphic on
        """
        _LOGGER.info("show_welcome called with: page=%s", page)
        command = f"<P{page}><FV>"
        return await self._send_command(command)

    async def send_formatted_message(
        self,
        page: str,
        segments: list[dict[str, Any]],
        function: str | None = None,
    ) -> bool:
        """Send a formatted message with multiple segments, each with their own styling."""
        message_parts = [f"<P{page}>"]

        if function:
            func_code = FUNCTIONS.get(function, function)
            message_parts.append(f"<{func_code}>")

        for segment in segments:
            if "graphic" in segment:
                message_parts.append(f"<B{segment['graphic']}>")

            elif "text" in segment:
                if "color" in segment:
                    color_code = COLORS.get(segment["color"], segment["color"])
                    message_parts.append(f"<{color_code}>")

                if "font" in segment:
                    font_code = FONTS.get(segment["font"], segment["font"])
                    message_parts.append(f"<{font_code}>")

                if "size" in segment:
                    size_code = SIZES.get(segment["size"], segment["size"])
                    message_parts.append(f"<{size_code}>")

                if "segment_function" in segment:
                    func_code = FUNCTIONS.get(segment["segment_function"], segment["segment_function"])
                    message_parts.append(f"<{func_code}>")

                # Add trailing space to text to prevent demo mode
                text = segment["text"]
                if not text.endswith(" "):
                    text = text + " "
                message_parts.append(text)

        command = "".join(message_parts)
        return await self._send_command(command)

    async def send_raw_protocol(
        self,
        page: str,
        protocol_string: str,
    ) -> bool:
        """Send a raw protocol string (without <IDxx> prefix)."""
        command = f"<P{page}>{protocol_string}"
        return await self._send_command(command)

    async def delete_page(self, page: str = "*") -> bool:
        """Delete a page or all pages."""
        command = f"<DP{page}>"
        return await self._send_command(command)

    async def delete_graphic(self, block: str = "*") -> bool:
        """Delete a graphic block or all graphics."""
        command = f"<DG{block}>"
        return await self._send_command(command)

    async def delete_all(self) -> bool:
        """Delete all pages and graphics."""
        command = "<D*>"
        return await self._send_command(command)

    async def run_page(self, page: str) -> bool:
        """Run a specific page now."""
        command = f"<RP{page}>"
        return await self._send_command(command)

    async def set_speed(self, speed: str | int) -> bool:
        """Set the shift speed (A=fastest, Z=slowest)."""
        if isinstance(speed, int):
            if 0 <= speed <= 25:
                speed = chr(65 + speed)
            else:
                _LOGGER.error("Speed must be between 0-25 or A-Z")
                return False

        command = f"<SPD{speed}>"
        return await self._send_command(command)

    async def set_time(self) -> bool:
        """Set the display's internal clock to current system time."""
        now = datetime.now()

        century = str(now.year // 100)
        year = f"{now.year % 100:02d}"
        month = f"{now.month:02d}"
        day = f"{now.day:02d}"
        weekday = str(now.weekday())
        hour = f"{now.hour:02d}"
        minute = f"{now.minute:02d}"
        second = f"{now.second:02d}"
        hour_format = "1"

        command = f"<TC{century}{year}{month}{day}{weekday}{hour}{minute}{second}{hour_format}>"
        return await self._send_command(command)

    async def create_graphic(self, block: str, pattern: str) -> bool:
        """Create a custom graphic block (18x7 dots, 126 bytes)."""
        if len(pattern) != 126:
            _LOGGER.error("Graphic pattern must be exactly 126 characters (18x7)")
            return False

        valid_chars = set("RGYB")
        if not all(c.upper() in valid_chars for c in pattern):
            _LOGGER.error("Graphic pattern must only contain R, G, Y, or B")
            return False

        command = f"<G{block}>{pattern.upper()}"
        return await self._send_command(command)

    async def get_sign_info(self) -> dict | None:
        """Get sign information from Faux-Lite device."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                async with self._session.get(f"{self._base_url}/api/info") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        _LOGGER.error("Failed to get device info: HTTP %s", response.status)
                        return None
        except Exception as err:
            _LOGGER.error("Error getting device info: %s", err)
            return None

    async def reset_sign(self) -> bool:
        """Reset the sign to factory default settings."""
        command = "<RST>"
        return await self._send_command(command)

    async def run_page_timed(self, page: str, times: int, next_page: str) -> bool:
        """Run a page for a specified number of times, then switch to another page."""
        command = f"<RP{page}><{times:02d}><RP{next_page}>"
        return await self._send_command(command)

    async def count_up(self, unit: str, start_value: int, target_value: int, target_page: str) -> bool:
        """Set up a count-up timer (days or hours)."""
        command = f"<U{unit}{start_value:04d}{target_value:04d}{target_page}>"
        return await self._send_command(command)

    async def count_down(self, days: int, hours: int, minutes: int, target_page: str) -> bool:
        """Set up a countdown timer."""
        command = f"<V{days:04d}{hours:02d}{minutes:02d}{target_page}>"
        return await self._send_command(command)

    async def test_connection(self) -> bool:
        """Test connectivity to the Faux-Lite device."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                async with self._session.get(f"{self._base_url}/api/info") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("device") == "faux-lite":
                            _LOGGER.info("Successfully connected to Faux-Lite device")
                            return True
                        else:
                            _LOGGER.error("Device at %s is not a Faux-Lite device", self._base_url)
                            return False
                    else:
                        _LOGGER.error("Failed to connect: HTTP %s", response.status)
                        return False
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout connecting to %s", self._base_url)
            return False
        except Exception as err:
            _LOGGER.error("Error testing connection: %s", err)
            return False

    async def close(self) -> None:
        """Close the connection (no-op for HTTP client)."""
        pass
