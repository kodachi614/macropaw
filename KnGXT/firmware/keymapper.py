from kmk.keys import KC


class Keymapper:
    """
    Keymapper is meant to cope with the problem that the keycodes the
    MacroPaw sends need to change depending on what how the OS's keymap is
    set. For example, if the OS is using a QWERTY keymap and you want a key
    on the MacroPaw to type an E, you just send KC.E (code 8). But if the OS
    is using a Dvorak keymap, you need to send KC.D (code 7). This is because
    (to use Unicode terminology) the keycodes don't represent codepoints, they
    represent physical positions on the keyboard, even though they're ordered
    (basically) alphabetically (at least when you're talking about letters).
    So you have to send KC.D to get an E with the Dvorak map because the key
    you press to get an E when you use Dvorak is in the same position as the
    key you press to get a D when you use QWERTY.

    Horrible, isn't it? We need a real way to just send Unicode codepoints...
    and there isn't a standard way to do that.

    When using a Keymapper, you can use square brace or dot notation, the
    same as the KC class -- so Keymapper["SPACE"] and Keymapper.SPACE are
    both valid. You can also use the mapped() method if you need to have a
    Callable for some reason.
    """
    _map = {}

    def mapped(self, key):
        return KC[self._map.get(key, key)]

    def __getitem__(self, key):
        return self.mapped(key)

    def __getattr__(self, key):
        return self.mapped(key)


class _QWERTY(Keymapper):
    """
    The QWERTY Keymapper is just a passthrough, since QWERTY is the layout
    the keycodes are based on in the first place.
    """
    pass


QWERTY = _QWERTY()


class _Dvorak(Keymapper):
    """
    The Dvorak Keymapper maps keycodes you want into the keycodes you need to
    send when the OS is using the Dvorak layout.
    """
    _map = {
        'MINUS': r"'",
        'MINS': r"'",
        '-': r"'",

        'UNDERSCORE': r'"',
        'UNDS': r'"',
        '_': r'"',

        'EQUAL': r']',
        'EQL': r']',
        '=': r']',

        'PLUS': r'}',
        '+': r'}',

        'LBRACKET': r'-',
        'LBRC': r'-',
        '[': r'-',

        'LEFT_CURLY_BRACE': r'_',
        'LCBR': r'_',
        '{': r'_',

        'RBRACKET': r'=',
        'RBRC': r'=',
        ']': r'=',

        'RIGHT_CURLY_BRACE': r'+',
        'RCBR': r'+',
        '}': r'+',

        'COLON': r'Z',
        'COLN': r'Z',
        ':': r'Z',

        'SEMICOLON': r'z',
        'SCOLON': r'z',
        'SCLN': r'z',
        ';': r'z',

        'DOUBLE_QUOTE': r'Q',
        'DQUO': r'Q',
        'DQT': r'Q',
        '"': r'Q',

        'QUOTE': r'q',
        'QUOT': r'q',
        "'": r'q',

        'GRAVE': '`',
        'GRV': '`',
        'ZKHK': '`',
        '`': '`',

        'COMMA': r'w',
        'COMM': r'w',
        ',': r'w',

        'LEFT_ANGLE_BRACKET': r'W',
        'LABK': r'W',
        '<': r'W',

        'DOT': r'e',
        '.': r'e',

        'RIGHT_ANGLE_BRACKET': r'E',
        'RABK': r'E',
        '>': r'E',

        'QUESTION': r'{',
        'QUES': r'{',
        '?': r'{',

        'SLASH': r'[',
        'SLSH': r'[',
        '/': r'[',

        r'b': r'n',
        r'B': r'N',
        r'c': r'i',
        r'C': r'I',
        r'd': r'h',
        r'D': r'H',
        r'e': r'd',
        r'E': r'D',
        r'f': r'y',
        r'F': r'Y',
        r'g': r'u',
        r'G': r'U',
        r'h': r'j',
        r'H': r'J',
        r'i': r'g',
        r'I': r'G',
        r'j': r'c',
        r'J': r'C',
        r'k': r'v',
        r'K': r'V',
        r'l': r'p',
        r'L': r'P',
        r'n': r'l',
        r'N': r'L',
        r'o': r's',
        r'O': r'S',
        r'p': r'r',
        r'P': r'R',
        r'q': r'x',
        r'Q': r'X',
        r'r': r'o',
        r'R': r'O',
        r's': r';',
        r'S': r':',
        r't': r'k',
        r'T': r'K',
        r'u': r'f',
        r'U': r'F',
        r'x': r'b',
        r'X': r'B',
        r'y': r't',
        r'Y': r'T',
        r'z': r"/",
        r'Z': r'?',
    }

Dvorak = _Dvorak()


def _FSKeymapper():
    keymap = "QWERTY"

    try:
        keymap = open("/keymap", "r").readline().strip()
    except:
        keymap = "QWERTY"

    mapper = globals().get(keymap, QWERTY)

    return mapper

FSKeymapper = _FSKeymapper()


if __name__ == "__main__":
    mapper = Dvorak

    vectors = [
        [ [ "j", "J" ], "c", "C" ],
        [ [ "l", "L" ], "p", "P" ],
        [ [ " ", "SPACE" ], " ", "SPACE" ],
        [ [ "i", "I" ], "g", "G" ],
        [ [ "m", "M" ], "m", "M" ],
        [ [ "o", "O" ], "s", "S" ],
        [ [ "b", "B" ], "n", "N" ],
        [ [ "x", "X" ], "b", "B" ],
        [ [ "z" ], "/", "SLASH" ],
        [ [ "Z" ], "?", "QUESTION" ],
        [ [ "s" ], ";", "SCOLON" ],
        [ [ "S" ], ":", "COLON" ],
        [ [ ".", "DOT" ], "e", "E" ],
        [ [ "+", "PLUS" ], "}", "RIGHT_CURLY_BRACE" ],
        [ [ "=", "EQUAL" ], "]", "RBRACKET" ],
        [ [ "-", "MINUS" ], "'", "QUOTE" ],
        [ [ "/", "SLASH" ], "[", "LBRACKET" ],
        [ [ "*" ], "*" ],
        [ [ "LEFT" ], "LEFT" ],
        [ [ "RIGHT" ], "RIGHT" ],
    ]

    for vector in vectors:
        dv = vector[0]
        wanted = vector[1:]

        for i in dv:
            got1 = mapper[i]
            got2 = getattr(mapper, i)

            if got1 != got2:
                print(f"array/getattr failed for {i}: {got1} != {got2}")

            for w in wanted:
                got3 = KC[w]

                if got1 != got3:
                    print(f"dv/qw failed for {i} and {w}: {got1} != {got3}")

