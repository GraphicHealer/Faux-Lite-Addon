"""Constants for the Prolite Display integration."""

DOMAIN = "prolite_display"

CONF_HOST = "host"
CONF_SIGN_ID = "sign_id"

DEFAULT_SIGN_ID = "01"
DEFAULT_PORT = 80

COLORS = {
    "dim_red": "CA",
    "red": "CB",
    "bright_red": "CC",
    "orange": "CD",
    "bright_orange": "CE",
    "light_yellow": "CF",
    "yellow": "CG",
    "bright_yellow": "CH",
    "lime": "CI",
    "dim_lime": "CJ",
    "bright_lime": "CK",
    "bright_green": "CL",
    "green": "CM",
    "dim_green": "CN",
    "yel_grn_red": "CO",
    "rainbow": "CP",
    "red_grn_3d": "CQ",
    "red_yel_3d": "CR",
    "grn_red_3d": "CS",
    "grn_yel_3d": "CT",
    "grn_on_red": "CU",
    "red_on_grn": "CV",
    "org_on_grn_3d": "CW",
    "lime_on_red_3d": "CX",
    "grn_on_red_3d": "CY",
    "red_on_grn_3d": "CZ",
}

FONTS = {
    "normal": "SA",
    "bold": "SB",
    "italic": "SC",
    "bold_italic": "SD",
    "flash_normal": "SE",
    "flash_bold": "SF",
    "flash_italic": "SG",
    "flash_bold_italic": "SH",
}

SIZES = {
    "5x7": "SI",
    "4x7": "SJ",
}

FUNCTIONS = {
    "auto": "FA",
    "open": "FB",
    "cover": "FC",
    "date": "FD",
    "cycling": "FE",
    "close_right": "FF",
    "close_left": "FG",
    "close_both": "FH",
    "scroll_up": "FI",
    "scroll_down": "FJ",
    "overlap": "FK",
    "stacking": "FL",
    "comic_1": "FM",
    "comic_2": "FN",
    "beep": "FO",
    "pause": "FP",
    "appear": "FQ",
    "random": "FR",
    "shift_left": "FS",
    "time": "FT",
    "magic": "FU",
    "thank_you": "FV",
    "welcome": "FW",
    "link_page": "FZ",
    "target": "F1",
    "current": "F2",
    "day_left": "F3",
    "hour_left": "F4",
    "minute_left": "F5",
    "second_left": "F6",
}

PAGES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
         "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

GRAPHICS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
            "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

SPEED_LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
                 "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
