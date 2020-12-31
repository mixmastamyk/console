'''
    ascii4 - "Þe Auld" Four-Column ASCII Table, FTW!
'''
from console import fg, bg, fx, defx
from console.detection import get_theme
from console.utils import make_hyperlink


ASCII_MODE = 1  # TODO: rm these
UNICODE_MODE = 2

_wp_base_url = 'https://en.wikipedia.org/wiki/'
# help styles
_d, n = fg.green, fx.end  # digit, normal
_bd = fx.bold + _d      # bold and/or bright digit
_i = fx.italic
_kb = fx.reverse  # keyboard

_help_text = __doc__ + f'''
    This four-column table (of thirty-two rows each) helps better illustrate
    relationships between characters and control codes:

        • To find the binary representation of a character, concatenate the
          two digit group code above its column, with its five digit row code:

          {_i}Optional 8th bit{n} →  {_d}0{n}  {_bd}10{n}  {_d}01000{n}        ⇒  {_d}0{_bd}10{n}{_d}01000{n}
                     {_i}Group code{n} ↗      ↑ {_i}Row code{n}      ↑ {_i}Full byte, aka "H"{n}

        • To generate a control code, a key is pressed then AND-ed with the
          control key group code of 00, forcing the sixth and seventh bits
          to zero.  This is why, for example:

          • {_i}BEL{n}, the Bell may be activated with {_kb}^G{n} {_i}(column to right){n}
          • {_i}BS{n}, the Backspace key is represented by {_kb}^H{n}
          • {_i}ESC{n}, the Escape key is represented by {_kb}^[{n} etc.

        • This is also why one can add 32/20h to the index of a capital to
          find the corresponding lower case letter.

    Arguments:
        link                Add hyperlinks to special characters.
        no-headers          Skip informative headers.
        unicode_symbols     Use symbols instead of names for control-chars.

    Note:
        The listing in this format is relatively tall and it is therefore
        difficult to see everything at once on terminals under ~thirty-two
        lines in height. The standard eight-column "ascii" command for
        Unix-likes is recommended under shorter terminals when a complete view
        is desired.
'''


# A range of 0…128, rendered in a table with four columns of 32 rows
index_table = (
    ( 0, 32, 64,  96),
    ( 1, 33, 65,  97),
    ( 2, 34, 66,  98),
    ( 3, 35, 67,  99),
    ( 4, 36, 68, 100),
    ( 5, 37, 69, 101),
    ( 6, 38, 70, 102),
    ( 7, 39, 71, 103),
    ( 8, 40, 72, 104),
    ( 9, 41, 73, 105),
    (10, 42, 74, 106),
    (11, 43, 75, 107),
    (12, 44, 76, 108),
    (13, 45, 77, 109),
    (14, 46, 78, 110),
    (15, 47, 79, 111),
    (16, 48, 80, 112),
    (17, 49, 81, 113),
    (18, 50, 82, 114),
    (19, 51, 83, 115),
    (20, 52, 84, 116),
    (21, 53, 85, 117),
    (22, 54, 86, 118),
    (23, 55, 87, 119),
    (24, 56, 88, 120),
    (25, 57, 89, 121),
    (26, 58, 90, 122),
    (27, 59, 91, 123),
    (28, 60, 92, 124),
    (29, 61, 93, 125),
    (30, 62, 94, 126),
    (31, 63, 95, 127),
)


ctrl_symbols = (
    ('00000', 'NUL', '␀', 'Null_character'),
    ('00001', 'SOH', '␁', 'C0_and_C1_control_codes#SOH'),
    ('00010', 'STX', '␂', 'C0_and_C1_control_codes#STX'),
    ('00011', 'ETX', '␃', 'C0_and_C1_control_codes#ETX'),
    ('00100', 'EOT', '␄', 'C0_and_C1_control_codes#EOT'),
    ('00101', 'ENQ', '␅', 'C0_and_C1_control_codes#ENQ'),
    ('00110', 'ACK', '␆', 'C0_and_C1_control_codes#ACK'),
    ('00111', 'BEL', '␇', 'C0_and_C1_control_codes#BEL'),
    ('01000', 'BS',  '␈', 'C0_and_C1_control_codes#BS'),
    ('01001', 'HT',  '␉', 'C0_and_C1_control_codes#HT'),
    ('01010', 'LF',  '␊', 'C0_and_C1_control_codes#LF'),
    ('01011', 'VT',  '␋', 'C0_and_C1_control_codes#VT'),
    ('01100', 'FF',  '␌', 'C0_and_C1_control_codes#FF'),
    ('01101', 'CR',  '␍', 'C0_and_C1_control_codes#CR'),
    ('01110', 'SO',  '␎', 'C0_and_C1_control_codes#SO'),
    ('01111', 'SI',  '␏', 'C0_and_C1_control_codes#SI'),
    ('10000', 'DLE', '␐', 'C0_and_C1_control_codes#DLE'),
    ('10001', 'DC1', '␑', 'C0_and_C1_control_codes#DC1'),
    ('10010', 'DC2', '␒', 'C0_and_C1_control_codes#DC2'),
    ('10011', 'DC3', '␓', 'C0_and_C1_control_codes#DC3'),
    ('10100', 'DC4', '␔', 'C0_and_C1_control_codes#DC4'),
    ('10101', 'NAK', '␕', 'C0_and_C1_control_codes#NAK'),
    ('10110', 'SYN', '␖', 'C0_and_C1_control_codes#SYN'),
    ('10111', 'ETB', '␗', 'C0_and_C1_control_codes#ETB'),
    ('11000', 'CAN', '␘', 'C0_and_C1_control_codes#CAN'),
    ('11001', 'EM',  '␙', 'C0_and_C1_control_codes#EM'),
    ('11010', 'SUB', '␚', 'C0_and_C1_control_codes#SUB'),
    ('11011', 'ESC', '␛', 'C0_and_C1_control_codes#ESC'),
    ('11100', 'FS',  '␜', 'C0_and_C1_control_codes#FS'),
    ('11101', 'GS',  '␝', 'C0_and_C1_control_codes#GS'),
    ('11110', 'RS',  '␞', 'C0_and_C1_control_codes#RS'),
    ('11111', 'US',  '␟', 'C0_and_C1_control_codes#US'),
    (None,    ' ',   '␠', 'Space_(punctuation)'),
    (None,    'DEL', '␡', 'Delete_character'),  # aka index -1
)


class SilentString(str):
    # Used when output is redirected.  Shouldn't be necessary, but here we are.
    def __call__(self, source):  # shaddup a ya face!
        return source


# TODO, separate building from printing
def print_ascii_chart(
        link=False,
        headers=True,
        unicode_symbols=False,
    ):
    # see module doc string
    mode = UNICODE_MODE if unicode_symbols else ASCII_MODE  # TODO
    try:
        # Get theme - defaults
        bin_clr = dec_clr = hex_clr = hdr_style = SilentString()
        evn_bg_clr = odd_bg_clr = ''

        theme = get_theme()
        if theme == 'dark':
            bin_clr = fg.darkred
            dec_clr = fg.darkorange3
            hex_clr = fg.purple
            evn_bg_clr = str(bg.i233)
            odd_bg_clr = str(bg.i235)
            hdr_style = bg.i235 + fx.italic

        elif theme == 'light':
            bin_clr = fg.blue
            dec_clr = fg.green
            hex_clr = fg.cyan
            evn_bg_clr = str(bg.i255)
            odd_bg_clr = str(bg.i253)
            hdr_style = bg.i253 + fx.italic

        if headers:
            ASCII = 'ASCII'
            if link:
                ASCII = make_hyperlink(_wp_base_url + 'ASCII', ASCII)
            print('\n                       ',
                fx.bold(f'Four-Column Grouped {ASCII} Table'), '\n'
            )
            Bin = bin_clr('Bin')
            Dc = dec_clr('Dc')
            Dec = dec_clr('Dec')
            Hx = hex_clr('Hx')
            d, n = fx.dim, defx.dim
            print(hdr_style(
                f' {Bin}    {Dc} {Hx}  {bin_clr("00")} {d}Ctrl{n}     '
                f'{Dc} {Hx}  {bin_clr("01")} {d}Punct{n}    '
                f'{Dc} {Hx}  {bin_clr("10")} {d}Upper{n}   '
                f'{Dec} {Hx} {bin_clr("11")} {d}Lower{n} '
            ))

        # print each row
        for row in index_table:
            columns = []
            row_num = row[0]
            if (row_num % 2) == 0:  # even
                columns.append(evn_bg_clr)
            else:  # odd
                columns.append(odd_bg_clr)

            for i in row:
                binary = ' '
                if mode is UNICODE_MODE:
                    padding = 2
                else:
                    padding = 3

                if i < 32:  # control chars + space
                    sinfo = ctrl_symbols[i]
                    binary = bin_clr(sinfo[0])
                    symbol = f'{sinfo[mode]:<{padding}}'
                    if mode is ASCII_MODE:  # add italic
                        symbol = fx.italic + symbol + defx.italic
                    if link:
                        symbol = make_hyperlink(_wp_base_url + sinfo[3], symbol)
                    if mode is UNICODE_MODE:  # short chars, add margin
                        symbol += ' '

                elif i == 32:  # space is unique
                    padding = 2  # always
                    sinfo = ctrl_symbols[i]
                    symbol = f'{sinfo[mode]:<{padding}}'
                    if link:
                        symbol = make_hyperlink(_wp_base_url + sinfo[3], symbol)
                        symbol += ' '

                elif i == 127:  # delete is unique
                    symbol = ctrl_symbols[-1][mode]
                    symbol = f'{symbol:<{padding}}'
                    if mode is ASCII_MODE:  # add italic
                        symbol = fx.italic + symbol + defx.italic
                    if link:
                        symbol = make_hyperlink(_wp_base_url + ctrl_symbols[-1][2],
                                                symbol)
                else:  # other groups
                    symbol =  f'{i:<3c}'

                record = (
                    f' {binary} {dec_clr}{i:>3} '
                    f'{hex_clr}{i:02x}{fg.default}  {symbol:<3}     '
                )
                columns.append(record)

            columns.append(str(bg.default))  # extra padding at end
            print(''.join(columns), end='')
            print(bg.default)

    except Exception as err:
        print(err)

    return ' ' if headers else ''  # quiets console-cli, empty avoids extra nl


print_ascii_chart.__doc__ = _help_text
