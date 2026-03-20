# Prolite Display - Complete Service Guide

This integration provides **full GUI control** of all Prolite TruColor II protocol features through Home Assistant service calls with dropdown selectors.

## 🎨 Message Services

### send_message
**Basic message with formatting** - All options use dropdown selectors!

```yaml
service: prolite_display.send_message
data:
  page: "A"              # Dropdown: A-Z
  text: "Hello World"
  color: "bright_red"    # Dropdown: 26 colors
  font: "bold"           # Dropdown: 8 fonts
  size: "5x7"            # Dropdown: 2 sizes
  function: "scroll_up"  # Dropdown: 30+ animations
```

**Available Colors** (dropdown):
- `dim_red`, `red`, `bright_red`
- `orange`, `bright_orange`
- `light_yellow`, `yellow`, `bright_yellow`
- `lime`, `dim_lime`, `bright_lime`
- `green`, `bright_green`, `dim_green`
- `rainbow`, `yel_grn_red`
- `red_grn_3d`, `red_yel_3d`, `grn_red_3d`, `grn_yel_3d`
- `grn_on_red`, `red_on_grn`
- `org_on_grn_3d`, `lime_on_red_3d`, `grn_on_red_3d`, `red_on_grn_3d`

**Available Fonts** (dropdown):
- `normal`, `bold`, `italic`, `bold_italic`
- `flash_normal`, `flash_bold`, `flash_italic`, `flash_bold_italic`

**Available Functions** (dropdown):
- `auto`, `open`, `cover`, `date`, `cycling`
- `close_right`, `close_left`, `close_both`
- `scroll_up`, `scroll_down`
- `overlap`, `stacking`
- `comic_1`, `comic_2`
- `beep`, `pause`, `appear`, `random`
- `shift_left`, `time`, `magic`
- `thank_you`, `welcome`
- `link_page`, `target`, `current`
- `day_left`, `hour_left`, `minute_left`, `second_left`

### send_formatted_message
**Multi-segment WYSIWYG messages** - Different colors/fonts per segment

```yaml
service: prolite_display.send_formatted_message
data:
  page: "A"
  function: "scroll_up"
  segments:
    - text: "TEMP: "
      color: "yellow"
      font: "normal"
    - text: "{{ states('sensor.temperature') }}°F"
      color: "bright_red"
      font: "bold"
    - graphic: "A"
    - text: " HUMID: "
      color: "bright_green"
      font: "normal"
    - text: "{{ states('sensor.humidity') }}%"
      color: "bright_green"
      font: "bold"
```

### send_raw_protocol
**Direct protocol control** - For advanced users

```yaml
service: prolite_display.send_raw_protocol
data:
  page: "A"
  protocol_string: "<FI><CC>ALERT <CE>MESSAGE"
```

## 📄 Page Management

### run_page
**Display a specific page** - Dropdown selector for pages

```yaml
service: prolite_display.run_page
data:
  page: "A"  # Dropdown: A-Z
```

### run_page_timed
**⭐ NEW: Display page for N times, then switch** - All dropdowns!

```yaml
service: prolite_display.run_page_timed
data:
  page: "A"           # Dropdown: A-Z
  times: 5            # Number slider: 1-99
  next_page: "B"      # Dropdown: A-Z
```

**Use Case**: Show weather on Page A 5 times, then switch to news on Page B

### delete_page
**Delete a page or all pages**

```yaml
service: prolite_display.delete_page
data:
  page: "*"  # "*" for all, or A-Z
```

## 🎨 Graphics Management

### create_graphic
**Create custom 18x7 pixel graphics** - Dropdown for block selection

```yaml
service: prolite_display.create_graphic
data:
  block: "A"  # Dropdown: A-Z
  pattern: |
    RRRRRRRRRRRRRRRRRR
    RRRRRRRRRRRRRRRRRR
    YYYYYYYYYYYYYYYYYY
    YYYYYYYYYYYYYYYYYY
    YYYYYYYYYYYYYYYYYY
    GGGGGGGGGGGGGGGGGG
    GGGGGGGGGGGGGGGGGG
```

Colors: `R`=Red, `G`=Green, `Y`=Yellow, `B`=Black

### delete_graphic
**⭐ NEW: Delete graphics** - Dropdown with "All Graphics" option

```yaml
service: prolite_display.delete_graphic
data:
  block: "*"  # Dropdown: "All Graphics" or A-Z
```

### delete_all
**⭐ NEW: Reset everything** - Delete all pages and restore default graphics

```yaml
service: prolite_display.delete_all
```

## ⏱️ Timer Services

### count_up
**⭐ NEW: Count-up timer** - All GUI controls!

```yaml
service: prolite_display.count_up
data:
  unit: "D"              # Dropdown: "Days" or "Hours"
  start_value: 1         # Number slider: 1-9999
  target_value: 100      # Number slider: 1-9999
  target_page: "B"       # Dropdown: A-Z
```

**Use Case**: Count days since last incident, switch to celebration page at 100 days

### count_down
**⭐ NEW: Countdown timer** - Number sliders for all values!

```yaml
service: prolite_display.count_down
data:
  days: 30        # Number slider: 0-9999
  hours: 12       # Number slider: 0-59
  minutes: 30     # Number slider: 0-59
  target_page: "C"  # Dropdown: A-Z
```

**Use Case**: Countdown to event, show special message when timer hits zero

## ⚙️ Display Settings

### set_speed
**Set scroll speed** - Number slider!

```yaml
service: prolite_display.set_speed
data:
  speed: 5  # Slider: 0-25 (0=fastest, 25=slowest)
```

### set_time
**Sync display clock with Home Assistant**

```yaml
service: prolite_display.set_time
```

### get_sign_info
**⭐ NEW: Get display information** - Returns baud rate, ID, version

```yaml
service: prolite_display.get_sign_info
```

## 🎯 Complete Protocol Coverage

This integration now supports **100% of the Prolite TruColor II protocol**:

✅ **Messages**: Text, colors, fonts, sizes, animations  
✅ **Pages**: 26 pages (A-Z), run, delete, timed rotation  
✅ **Graphics**: 26 custom blocks, create, delete  
✅ **Timers**: Count up, count down with target pages  
✅ **Settings**: Speed, time sync, sign info  
✅ **Advanced**: Raw protocol, formatted segments  

## 🎨 GUI Features

All services use **Home Assistant's native selectors**:

- **Dropdown menus** for pages, colors, fonts, functions, graphics
- **Number sliders** for speed, timers, counts
- **Text areas** for messages and patterns
- **Custom values** allowed where appropriate

No typing codes - everything is point-and-click!

## 📱 Example Automations

### Weather Display with Auto-Rotation
```yaml
automation:
  - alias: "Weather Display Rotation"
    trigger:
      - platform: time_pattern
        minutes: "/5"
    action:
      # Show current weather 3 times
      - service: prolite_display.send_message
        data:
          page: "A"
          text: "{{ states('sensor.temperature') }}°F"
          color: "bright_red"
          font: "bold"
          function: "scroll_up"
      
      # Then rotate to forecast
      - service: prolite_display.run_page_timed
        data:
          page: "A"
          times: 3
          next_page: "B"
```

### Event Countdown
```yaml
automation:
  - alias: "Christmas Countdown"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: prolite_display.count_down
        data:
          days: "{{ (as_timestamp('2024-12-25') - now().timestamp()) / 86400 | int }}"
          hours: 0
          minutes: 0
          target_page: "C"  # Christmas message page
```

### Multi-Color Status
```yaml
automation:
  - alias: "System Status Display"
    trigger:
      - platform: state
        entity_id: binary_sensor.door
    action:
      - service: prolite_display.send_formatted_message
        data:
          page: "A"
          function: "scroll_up"
          segments:
            - text: "DOOR: "
              color: "yellow"
              font: "normal"
            - text: "{{ 'OPEN' if is_state('binary_sensor.door', 'on') else 'CLOSED' }}"
              color: "{{ 'bright_red' if is_state('binary_sensor.door', 'on') else 'bright_green' }}"
              font: "flash_bold"
```

## 🔧 Tips

1. **Use dropdowns** - No need to memorize codes
2. **Test with Developer Tools** - Try services before automations
3. **Combine timers with pages** - Create dynamic displays
4. **Use templates** - Make messages dynamic with sensor data
5. **Layer segments** - Build complex multi-color messages

All features are accessible through the GUI - no YAML editing required for basic use!
