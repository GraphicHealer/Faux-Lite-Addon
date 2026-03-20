# Faux-Lite Display - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> **⚠️ FIRMWARE REQUIRED:** This integration requires the [Faux-Lite Firmware](https://github.com/GraphicHealer/Faux-Lite-Firmware) to be installed on an ESP32 connected to your Pro-Lite display. The firmware acts as a WiFi-to-Serial bridge that this integration communicates with. Please set up the firmware first before installing this integration.

Control your Pro-Lite LED display directly from Home Assistant with full service call support, entities, and automations.

## Features

- 🎯 **Service Calls** - Send messages, set colors, fonts, animations
- 🎨 **Entity Controls** - Select entities for colors, fonts, functions, and pages
- 📝 **Text Entity** - Store and manage page content
- 🔢 **Number Entity** - Control scroll speed
- 🔍 **Auto-Discovery** - Automatically finds Faux-Lite devices on your network
- 📡 **Multiple Services** - 20+ service calls for complete display control
- 🔊 **Beep Support** - Audible notifications
- ⏰ **Time & Date** - Display current time and date
- 🎭 **Special Functions** - Thank You, Welcome messages, and more

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the 3 dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL: `https://github.com/GraphicHealer/Faux-Lite-Addon`
5. Select category: "Integration"
6. Click "Add"
7. Search for "Faux-Lite Display" in HACS
8. Click "Download"
9. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/fauxlite_display` folder
2. Copy it to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

### Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Faux-Lite Display"
4. The integration will automatically scan for devices
5. Select your device from the list or enter IP manually
6. Click **Submit**

### Requirements

- Faux-Lite firmware running on ESP32 connected to Pro-Lite display
- Device must be on the same network as Home Assistant

## Entities

Once configured, the integration creates the following entities:

### Select Entities
- **Color** - Choose display color (Dim Red, Red, Bright Yellow, etc.)
- **Font** - Choose font style (Normal, Bold, Italic, Flash, etc.)
- **Function** - Choose animation (Auto, Open, Cover, Scroll, etc.)
- **Active Page** - Select which page to display (A-Z)

### Text Entity
- **Page Text** - Set the text content for the selected page

### Number Entity
- **Scroll Speed** - Control scroll speed (1-5)

## Service Calls

### Basic Message Services

#### `fauxlite_display.send_message`
Send a one-shot message that displays and then clears.

```yaml
service: fauxlite_display.send_message
data:
  text: "Hello World"
  color: "bright_yellow"
  font: "bold"
  function: "scroll_up"
  exit_function: "appear"
  beep: true
  repeat: 3
```

#### `fauxlite_display.set_message`
Set a message on a specific page (persistent).

```yaml
service: fauxlite_display.set_message
data:
  page: "A"
  text: "Welcome Home"
  color: "bright_green"
  font: "bold"
  function: "appear"
  beep: false
```

#### `fauxlite_display.send_formatted_message`
Send a message with multiple segments, each with different styling.

```yaml
service: fauxlite_display.send_formatted_message
data:
  page: "B"
  segments:
    - text: "Temperature: "
      color: "bright_yellow"
      font: "normal"
    - text: "72°F"
      color: "bright_red"
      font: "bold"
  function: "appear"
```

### Display Control Services

#### `fauxlite_display.run_page`
Display a specific page.

```yaml
service: fauxlite_display.run_page
data:
  page: "A"
```

#### `fauxlite_display.run_page_timed`
Display a page for a specific duration.

```yaml
service: fauxlite_display.run_page_timed
data:
  page: "A"
  times: 5
```

#### `fauxlite_display.delete_page`
Clear a page or all pages.

```yaml
service: fauxlite_display.delete_page
data:
  page: "A"  # Use "*" for all pages
```

### Special Function Services

#### `fauxlite_display.send_beep`
Send an audible beep.

```yaml
service: fauxlite_display.send_beep
data:
  count: 3
```

#### `fauxlite_display.show_time`
Display the current time.

```yaml
service: fauxlite_display.show_time
data:
  page: "A"
```

#### `fauxlite_display.show_date`
Display the current date.

```yaml
service: fauxlite_display.show_date
data:
  page: "A"
```

#### `fauxlite_display.pause_display`
Pause the current display.

```yaml
service: fauxlite_display.pause_display
data:
  page: "A"
```

#### `fauxlite_display.show_thank_you`
Display the THANK YOU graphic.

```yaml
service: fauxlite_display.show_thank_you
data:
  page: "A"
```

#### `fauxlite_display.show_welcome`
Display the WELCOME graphic.

```yaml
service: fauxlite_display.show_welcome
data:
  page: "A"
```

### Advanced Services

#### `fauxlite_display.send_raw_protocol`
Send raw Pro-Lite protocol commands.

```yaml
service: fauxlite_display.send_raw_protocol
data:
  page: "A"
  protocol_string: "<CH><SA>Custom Command"
```

#### `fauxlite_display.set_speed`
Set scroll speed.

```yaml
service: fauxlite_display.set_speed
data:
  speed: 3
```

#### `fauxlite_display.set_time`
Set the display's internal clock.

```yaml
service: fauxlite_display.set_time
data:
  hour: 14
  minute: 30
```

#### `fauxlite_display.create_graphic`
Create a custom graphic.

```yaml
service: fauxlite_display.create_graphic
data:
  block: "A"
  dots: "FFFFFFFFFFFFFFFF"
```

## Automation Examples

### Welcome Home Message

```yaml
automation:
  - alias: "Welcome Home"
    trigger:
      - platform: state
        entity_id: person.john
        to: "home"
    action:
      - service: fauxlite_display.send_message
        data:
          text: "Welcome Home, John!"
          color: "bright_yellow"
          function: "appear"
          beep: true
```

### Temperature Display

```yaml
automation:
  - alias: "Update Temperature Display"
    trigger:
      - platform: state
        entity_id: sensor.living_room_temperature
    action:
      - service: fauxlite_display.send_formatted_message
        data:
          page: "A"
          segments:
            - text: "Temp: "
              color: "bright_yellow"
            - text: "{{ states('sensor.living_room_temperature') }}°F"
              color: "bright_red"
              font: "bold"
          function: "appear"
```

### Doorbell Notification

```yaml
automation:
  - alias: "Doorbell Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell
        to: "on"
    action:
      - service: fauxlite_display.send_message
        data:
          text: "DOORBELL"
          color: "bright_red"
          font: "bold"
          function: "stacking"
          beep: true
          repeat: 5
```

### Time Display Every Hour

```yaml
automation:
  - alias: "Show Time Hourly"
    trigger:
      - platform: time_pattern
        minutes: 0
    action:
      - service: fauxlite_display.show_time
        data:
          page: "A"
```

## Available Colors

- `dim_red`, `red`, `bright_red`
- `orange`, `bright_orange`
- `light_yellow`, `yellow`, `bright_yellow`
- `lime`, `dim_lime`, `bright_lime`
- `bright_green`, `green`, `dim_green`
- `rainbow`, `yellow_green_red`
- And more...

## Available Fonts

- `normal`, `bold`, `italic`, `bold_italic`
- `flash_normal`, `flash_bold`, `flash_italic`, `flash_bold_italic`

## Available Animations

- `auto`, `open`, `cover`, `cycling`
- `close_right`, `close_left`, `close_both`
- `scroll_up`, `scroll_down`
- `overlap`, `stacking`, `appear`
- `random`, `shift_left`, `magic`

## Protocol Documentation

For complete details on the Pro-Lite ASCII-Series Version 6.00 protocol, see the [official protocol PDF](docs/Protocols_TruColorII_6.0.pdf) included in this repository. This comprehensive document provides:

- **Complete command reference** - All available protocol commands with exact syntax
- **Color codes** - Full list of color combinations and 3D effects
- **Font specifications** - All font styles, sizes, and flash modes
- **Animation details** - Timing and behavior of all transition effects
- **Page management** - Advanced page chaining and linking
- **Special functions** - Time, date, counters, graphics, and more
- **Serial specifications** - Baud rates, data format, and communication details

This PDF is the authoritative reference for understanding what commands the integration sends to your display and how to use advanced features.

## Troubleshooting

**Integration not finding device:**
- Ensure device is powered on and connected to network
- Check that device is accessible at its IP address
- Verify `/api/info` endpoint returns `{"device": "faux-lite"}`

**Service calls not working:**
- Check Home Assistant logs for errors
- Verify device IP hasn't changed
- Test with raw protocol service first

**Entities not updating:**
- Reload the integration
- Restart Home Assistant
- Check device is responding to API calls

## Firmware

This integration requires the Faux-Lite firmware running on an ESP32, wired to a Pro-Lite display compatible with the V6 protocol. Get the firmware here:
[Faux-Lite Firmware](https://github.com/GraphicHealer/Faux-Lite-Firmware)

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check the [Service Guide](custom_components/fauxlite_display/SERVICE_GUIDE.md) for detailed documentation

## License

MIT License - See LICENSE file for details

## Acknowledgments

This project was developed with the assistance of Cascade AI (Windsurf IDE).
