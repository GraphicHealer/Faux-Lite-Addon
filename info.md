# Faux-Lite Display Integration

Control your Pro-Lite LED display directly from Home Assistant.

## Features

- 🎯 **20+ Service Calls** - Complete display control
- 🎨 **Entity Controls** - Select colors, fonts, animations
- 🔍 **Auto-Discovery** - Finds devices automatically
- 📡 **REST API Integration** - Fast and reliable
- 🔊 **Beep Support** - Audible notifications
- ⏰ **Time & Date Display** - Built-in functions
- 🎭 **Special Graphics** - Thank You, Welcome messages

## Quick Start

1. Install via HACS
2. Add integration from Settings → Devices & Services
3. Select discovered device or enter IP manually
4. Start controlling your display!

## Basic Usage

### Send a Message

```yaml
service: fauxlite_display.send_message
data:
  text: "Hello World"
  color: "bright_yellow"
  function: "appear"
```

### Set Page Content

```yaml
service: fauxlite_display.set_message
data:
  page: "A"
  text: "Welcome Home"
  color: "bright_green"
```

### Display Time

```yaml
service: fauxlite_display.show_time
data:
  page: "A"
```

## Requirements

- Faux-Lite firmware on ESP32
- Pro-Lite ASCII-Series display
- Device on same network as Home Assistant

## Documentation

Full documentation available in the [README](https://github.com/GraphicHealer/fauxlite-hacs/blob/main/README.md)
