import os as _os
import re as _re
import sys as _sys
import tty as _tty
import termios as _termios

from enum import Enum

# Coordinates order are : (x_columns, y_row)

class LCCException(Exception):
    pass

class _Color():
    pass

class _ForegroundColor(_Color):
    pass

class _BackgroundColor(_Color):
    pass

class _Color256b(_Color):
    
    def __init__(self, r, g, b):
        for i in r, g, b:
            if i < 0 or i > 255 :
                raise LCCException("LCC Error : r, g and b must not be greater than 255 or less than 0.")
        self.r = r
        self.g = g
        self.b = b

class _ForegroundColor256(_Color256b, _ForegroundColor):
    pass

class _BackgroundColor256(_Color256b, _BackgroundColor):
    pass

class _ForegroundNormalColor(_ForegroundColor, Enum):
    black = 30
    red = 31
    green = 32
    brown = 33
    blue = 34
    magenta = 35
    cyan = 36
    white = 37

class _ForegroundBrightColor(_ForegroundColor, Enum):
    black = 90
    red = 91
    green = 92
    brown = 93
    blue = 94
    magenta = 95
    cyan = 96
    white = 97

class _BackgroundColor(_BackgroundColor, Enum):
    black = 40
    red = 41
    green = 42
    brown = 43
    blue = 44
    magenta = 45
    cyan = 46
    white = 47

class _TextFormat(Enum):
    reset = 0
    bold_on = 1
    half_bright_on = 2
    italic_on = 3
    underline_on = 4
    blink_on = 5
    reversecolors_on = 7
    primary_font = 10
    first_alternate_font = 11
    second_alternate_font = 12
    underlineX2_on = 21
    reset_intensity = 22
    italic_off = 23
    underline_off = 24
    blink_off = 25
    reverse_off = 27

class _Bright(Enum):
    light = 0
    normal = 1
    bold = 2

class _Underline(Enum):
    none = 0
    simple = 1
    double = 2

class Param():
    ForegroundNormalColor = _ForegroundNormalColor
    ForegroundBrightColor = _ForegroundBrightColor
    ForegroundColor256 = _ForegroundColor256
    BackgroundColor = _BackgroundColor
    BackgroundColor256 = _BackgroundColor256
    Bright = _Bright
    Underline = _Underline
    

class Cursor:

    def up(n=1):
        print("\x1b[{}A".format(n), end='')

    def down(n=1):
        print("\x1b[{}E".format(n), end='')

    def left(n=1):
        print("\x1b[{}D".format(n), end='')

    def right(n=1):
        print("\x1b[{}C".format(n), end='')

    def to_column(x):
        print("\x1b[{}G".format(x), end='')

    def to_row(x):
        print("\x1b[{}d".format(x), end='')

    def to_coordinate(column, row):
        print("\x1b[{ROW};{COLUMN}H".format(ROW=row, COLUMN=column), end='')
    
    def get_location():
        buff = ''
        stdin = _sys.stdin.fileno()
        tattr = _termios.tcgetattr(stdin)

        try:
            _tty.setcbreak(stdin, _termios.TCSANOW)
            _sys.stdout.write('\033[6n')
            _sys.stdout.flush()

            while True:
                buff += _sys.stdin.read(1)
                if buff[-1] == 'R':
                    break
        finally:
            _termios.tcsetattr(stdin, _termios.TCSANOW, tattr)
        matches = _re.match(r'^\033\[(\d*);(\d*)R', buff)
        if matches == None:
            return None
        groups = matches.groups()
        return (int(groups[1]), int(groups[0]))

    def save_location():
        print("\x1b[s", end="")

    def load_location():
        print("\x1b[u", end="")

class Erase:

    def from_cursor_to_displayend():
        print("\x1b[J", end="")

    def from_displaystart_to_cursor():
        print("\x1b[1J", end="")

    def display(scrollback=False):
        if scrollback:
            print("\x1b[3J", end="")
        else:
            print("\x1b[2J", end="")

    def from_cursor_to_rowend():
        print("\x1b[K", end="")

    def from_rowstart_to_cursor():
        print("\x1b[1K", end="")

    def row():
        print("\x1b[2K", end="")


def format(text, foreground: _ForegroundColor=Param.ForegroundNormalColor.white, background: Param.BackgroundColor=Param.BackgroundColor.black, italic=False, underline=Param.Underline.none, blink=False, bright=Param.Bright.normal) -> str:
    if isinstance(foreground, _Color256b):
        fstring = "\x1b[38;2;{R};{G};{B}".format(R=foreground.r, G=foreground.g, B=foreground.b)
    else:
        fstring = "\x1b[{}".format(foreground.value)

    if isinstance(background, _Color256b):
        fstring += ";48;2;{R};{G};{B}".format(R=background.r, G=background.g, B=background.b)
    else:
        fstring += ";{}".format(background.value)

    if italic:
        fstring += ";{}".format(_TextFormat.italic_on.value)
    if underline == _Underline.simple:
        fstring += ";{}".format(_TextFormat.underline_on.value)
    elif underline == _Underline.double:
        fstring += ";{}".format(_TextFormat.underlineX2_on.value)
    if blink:
        fstring += ";{}".format(_TextFormat.blink_on.value)
    if bright == _Bright.light:
        fstring += ";{}".format(_TextFormat.half_bright_on.value)
    elif bright == _Bright.bold:
        fstring += ";{}".format(_TextFormat.bold_on.value)
    return "{FSTRING}m{TEXT}\x1b[{RST};m".format(FSTRING=fstring, TEXT=text, RST=_TextFormat.reset.value)

def get_display_size():
    _os.get_terminal_size()
    
