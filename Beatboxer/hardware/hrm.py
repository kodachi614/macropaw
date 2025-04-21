import sys

import json
import re

from pyparsing import ParseResults, nestedExpr


def lisp(x):
    if isinstance(x, ParseResults):
        return lisp(list(x))

    if isinstance(x, list):
        assert(not isinstance(x[0], list))
        s = "(%s" % x[0]

        for y in x[1:]:
            s2 = lisp(y)

            if s2[0] == "(":
                s += "\n" + s2
            else:
                s += " " + s2

        s += ")"
    else:
        s = str(x)

    return s


class Size:
    def __init__(self, elements):
        self.width = elements[1]
        self.height = elements[2]

    def as_list(self):
        return ["size", self.width, self.height]


class Font:
    def __init__(self, elements):
        self.size = None
        self.thickness = None
        self.elements = []

        for el in elements[1:]:
            if el[0] == "size":
                self.size = Size(el)
            elif el[0] == "thickness":
                self.thickness = el[1]
            else:
                self.elements.append(el)

    def as_list(self):
        result = ["font"]
        if self.size:
            result.append(self.size.as_list())
        if self.thickness:
            result.append(["thickness", self.thickness])
        for el in self.elements:
            result.append(el)
        return result


class Effects:
    def __init__(self, elements):
        self.font = None
        self.elements = []

        for el in elements[1:]:
            if el[0] == "font":
                self.font = Font(el)
            else:
                self.elements.append(el)

    def as_list(self):
        result = ["effects"]

        if self.font:
            result.append(self.font.as_list())

        for el in self.elements:
            result.append(el)

        return result


class Location:
    def __init__(self, elements):
        self.x = elements[1]
        self.y = elements[2]
        self.rotation = None
        self.elements = []

        if len(elements) > 3:
            self.rotation = elements[3]

            if len(elements) > 4:
                self.elements = elements[4:]

    def as_list(self):
        result = ["at", self.x, self.y]

        if self.rotation is not None:
            result.append(self.rotation)

        for el in self.elements:
            result.append(el)

        return result


class Property:
    def __init__(self, elements):
        self.name = elements[1]
        self.value = elements[2]
        self.location = None
        self.effects = None
        self.elements = []

        for el in elements[3:]:
            if el[0] == "at":
                self.location = Location(el)
            elif el[0] == "effects":
                self.effects = Effects(el)

    def __str__(self):
        s = f"property {self.name} {self.value}"

        if self.location:
            s += f" @ {self.location.x} {self.location.y}"

            if self.location.rotation is not None:
                s += f", {self.location.rotation} degrees"

        if self.effects:
            s += f"\n    effects: {self.effects}"

        return s

    def as_list(self):
        result = ["property", self.name, self.value]

        if self.location:
            result.append(self.location.as_list())

        if self.effects:
            result.append(self.effects.as_list())

        for el in self.elements:
            result.append(el)

        return result

class GRText:
    def __init__(self, elements):
        self.text = elements[1]
        self.location = None
        self.properties = []
        self.elements = []

        for el in elements[2:]:
            if el[0] == "at":
                self.location = Location(el)
            elif el[0] == "effects":
                self.effects = Effects(el)
            else:
                self.elements.append(el)

    def as_list(self):
        result = ["gr_text", self.text]

        if self.location:
            result.append(self.location.as_list())

        if self.effects:
            result.append(self.effects.as_list())

        for el in self.elements:
            result.append(el)

        return result


class Footprint:
    def __init__(self, elements):
        self.kind = elements[1]
        self.location = None
        self.reference = None
        self.value = None
        self.properties = []
        self.elements = []

        for el in elements[2:]:
            if el[0] == "at":
                self.location = Location(el)
            elif el[0] == "property":
                p = Property(el)

                if p.name == '"Reference"':
                    self.reference = p
                elif p.name == '"Value"':
                    self.value = p
                else:
                    self.properties.append(p)
            else:
                self.elements.append(el)

    def __str__(self):
        s = f"footprint {self.kind}"

        if self.location:
            s += f" @ {self.location.x} {self.location.y}"

            if self.location.rotation is not None:
                s += f", {self.location.rotation} degrees"

        if self.reference:
            s += f"\n    reference: {self.reference.name} {self.reference.value}"

        if self.value:
            s += f"\n    value: {self.value.name} {self.value.value}"

        for p in self.properties:
            s += f"\n    property: {p.name} {p.value}"

        return s

    def as_list(self):
        result = ["footprint", self.kind]

        if self.location:
            result.append(self.location.as_list())

        if self.reference:
            result.append(self.reference.as_list())

        if self.value:
            result.append(self.value.as_list())

        for p in self.properties:
            result.append(p.as_list())

        for el in self.elements:
            result.append(el)

        return result


pcbData = open(sys.argv[1]).read()
pcbFile = nestedExpr().parseString(pcbData)
pcb = pcbFile[0]

found_kicad = False

interesting = {}
uninteresting = []
elements = []

for el in pcb:
    if not found_kicad:
        if el == "kicad_pcb":
            found_kicad = True
        else:
            raise Exception("Not a KiCad PCB file")
        continue

    if el[0] == "footprint":
        key = None
        fp = Footprint(el)

        match = re.match(r'^"(D\d+)"$', fp.reference.value)

        if not match:
            match = re.match(r'^"(SW\d+)"$', fp.reference.value)

            if match:
                switch_num = int(match.group(1)[2:])

                if switch_num < 1 or switch_num > 64:
                    match = None

        if match:
            key = f"FP {match.group(1)}"

            sys.stderr.write(f"Mark {key} at {fp.location.x} {fp.location.y} {fp.location.rotation}\n")
            interesting[key] = fp
        else:
            sys.stderr.write(f"Skip footprint {fp.reference.value} at {fp.location.x} {fp.location.y} {fp.location.rotation}\n")

            uninteresting.append(fp)
    elif el[0] == "gr_text":
        key = None
        gr_text = GRText(el)

        match = re.match(r'^"(SW\d+)"$', gr_text.text)

        if match:
            key = f"GRTXT {match.group(1)}"

        if key:
            sys.stderr.write(f"Mark {key} at {gr_text.location.x} {gr_text.location.y} {gr_text.location.rotation}\n")

            interesting[key] = gr_text
        else:
            sys.stderr.write(f"Skip gr_text {gr_text.text} at {gr_text.location.x} {gr_text.location.y} {gr_text.location.rotation}\n")

            uninteresting.append(gr_text)
    else:
        elements.append(el)

for k, v in interesting.items():
    match = re.match(r'^FP SW(\d+)$', k)

    if match:
        switchNum = int(match.group(1))

        row = (switchNum - 1) // 8
        col = (switchNum - 1) % 8

        x = 60.42 + (15 * col)
        y = 26.91 + (15 * row)

        v.location.x = x
        v.location.y = y

        v.reference.effects.font.size.width = 0.7
        v.reference.effects.font.size.height = 0.7

        # Yuck. The width of the text is about 0.7mm per character (good,
        # since that's a measured value that lines up with the font.size.width
        # above!) and the footprint is about 6.9mm wide. So... do the math for
        # the X placement.
        text_width = 0.7 * len(v.reference.value)
        space = (6.9 - text_width) / 2

        # This 0.25 is a measured fudge factor.
        v.reference.location.x = -1 * (space - 0.25)
        v.reference.location.y = -2.79
        v.reference.location.rotation = 0

        sys.stderr.write(f"Switch {v.reference.value}: {v.location.x} {v.location.y}\n")

for k, v in interesting.items():
    match = re.match(r'^FP D(\d+)$', k)

    if match:
        diodeNum = int(match.group(1))
        switchKey = f'FP SW{diodeNum}'

        switch = interesting[switchKey]

        x = switch.location.x + 5.55
        y = switch.location.y + 1.6275

        v.location.x = x
        v.location.y = y
        v.location.rotation = 90

        v.reference.effects.font.size.width = 0.7
        v.reference.effects.font.size.height = 0.7
        v.reference.location.x = 2.1775
        v.reference.location.y = 0.07
        v.reference.location.rotation = 0

        sys.stderr.write(f"Diode {v.reference.value}: {v.location.x} {v.location.y}\n")
        continue

    match = re.match(r'^GRTXT SW(\d+)$', k)

    if match:
        diodeNum = int(match.group(1))
        switchKey = f'FP SW{diodeNum}'

        switch = interesting[switchKey]

        # Yuck. The width of the text is about 0.7mm per character (good,
        # since that's a measured value that lines up with the font.size.width
        # above!) and the footprint is about 6.9mm wide. So... do the math for
        # the X placement.
        text_width = 0.7 * len(v.text)
        space = (6.9 - text_width) / 2

        # This 0.25 is a measured fudge factor.
        v.location.x = switch.location.x - (space - 0.25)
        v.location.y = switch.location.y - 2.78
        v.location.rotation = 0

        v.effects.font.size.width = 0.7
        v.effects.font.size.height = 0.7

        sys.stderr.write(f"Back label {v.text}: {v.location.x} {v.location.y}\n")

out = ["kicad_pcb"]

for el in elements:
    out.append(el)

for v in interesting.values():
    out.append(v.as_list())

for v in uninteresting:
    out.append(v.as_list())

print(lisp(out))
