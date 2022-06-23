#!/usr/bin/env python

import sys

import re

reAt = re.compile(r'^\(at (\d+(\.\d+)?) (\d+(\.\d+)?)( ([-+]?\d+(\.\d+)?))?\)$')
reText = re.compile(r'^\(fp_text ([^ ]+) \"([^"]+)\" \(at ([-+]?\d+(\.\d+)?) ([-+]?\d+(\.\d+)?)( ([-+]?\d+(\.\d+)?))?\) \(layer \"([^"]+)\"\)( hide)?$')
reIndent = re.compile(r'^\s+')
reDiode = re.compile(r'^D\d+$')
reCap = re.compile(r'^C\d+$')

class Text:
    def __init__(self, idx, groups):
        name, value, x, _, y, _, _, rot, _, layer, hide = groups

        self.name = name
        self.value = value
        self.x = float(x)
        self.y = float(y)
        self.rot = float(rot) if rot is not None else 0.0
        self.layer = layer
        self.idx = idx
        self.hide = True if hide else False
        self.mirror = False

    def line(self, indent):
        rstr = f' {self.rot}' if (self.rot != 0.0) else ''
        hstr = ' hide' if self.hide else ''
        mstr = ' *mirror*' if self.mirror else ''
        return f'{indent}(fp_text {self.name} "{self.value}" (at {self.x} {self.y}{rstr}) (layer "{self.layer}"){hstr}{mstr}\n'


class Footprint:
    def __init__(self, line):
        self.x = None
        self.y = None
        self.rot = None
        self.text = []
        self.name = None
        self.lines = [ line ]

    def locate(self, line, groups):
        x, _, y, _, _, rot, _ = groups
        self.x = float(x)
        self.y = float(y)
        self.rot = float(rot) if rot is not None else 0.0
        self.addLine(line)

    def addLine(self, line):
        self.lines.append(line)

    def addText(self, line, groups):
        t = Text(len(self.lines), groups)

        self.addLine(line)
        self.text.append(t)

        if t.name == 'reference':
            self.name = t.value

        if self.name == 'NP24':
            sys.stderr.write(f"-- ADD {t.name} {t.value}\n")


    def fixText(self, t, **args):
        for k, v in args.items():
            setattr(t, k, v)

        m = reIndent.match(self.lines[t.idx])
        indent = m.string[m.start():m.end()]

        self.lines[t.idx] = t.line(indent)

    def rectify(self):
        if self.name and self.name.startswith('NP'):
            # print(f"RECTIFY {self.name}")

            for t in self.text:
                if self.name == "NP24":
                    sys.stderr.write(f"-- RECTIFY {t.name} {t.value}\n")
                if t.name == "reference":
                    self.fixText(t, layer="F.SilkS", x=-1.65, y=-1.05)
                elif t.name == "value":
                    self.fixText(t, layer="F.SilkS", x=1.25,  y=-1.05, hide=False)
                elif (t.name == "user") and (t.value != "${REFERENCE}"):
                    self.fixText(t, layer="F.SilkS", x=-2.25,  y=0.7)

        # if self.name.startswith('SW'):
        #     # print(f"RECTIFY {self.name}")

        #     for t in self.text:
        #         if t.name == "reference":
        #             self.fixText(t, layer="F.SilkS", x=-6.775, y=-7.45)
        #         elif t.name == "value":
        #             self.fixText(t, hide=True)
        #         elif (t.name == "user") and (t.value == "${REFERENCE}"):
        #             self.fixText(t, layer="B.SilkS", x=3.8618,  y=-7.3312, mirror=True)

        # if self.name.startswith('TP'):
        #     # print(f"RECTIFY {self.name}")

        #     for t in self.text:
        #         if t.name == "reference":
        #             self.fixText(t, layer="F.SilkS", x=0, y=-2.0875)
        #         elif t.name == "value":
        #             self.fixText(t, hide=True)
        #         elif (t.name == "user") and (t.value == "${REFERENCE}"):
        #             self.fixText(t, layer="B.SilkS", x=0,  y=-2.0875, mirror=True)

        # if self.name and reDiode.match(self.name):
        #     # print(f"RECTIFY {self.name}")

        #     for t in self.text:
        #         if t.name == "reference":
        #             self.fixText(t, layer="F.SilkS", x=1.79, y=0.72, rot=180.0)
        #         elif t.name == "value":
        #             self.fixText(t, layer="F.SilkS", x=-1.86, y=0.27, rot=180.0)

        # if self.name and reCap.match(self.name):
        #     # print(f"RECTIFY {self.name}")

        #     for t in self.text:
        #         if t.name == "reference":
        #             self.fixText(t, layer="F.SilkS", x=-0.6158, y=-0.6396)
        #         elif t.name == "value":
        #             self.fixText(t, layer="F.SilkS", x=0.4764, y=-0.6396)

    def __str__(self) -> str:
        s = f"footprint {self.name} @ {self.x} {self.y} {self.rot}\n"

        for t in self.text:
            s += f"    text {t.name} '{t.value}' at {t.layer} {t.x} {t.y} {t.rot}\n"

        return s

    def dump(self):
        for l in self.lines:
            sys.stdout.write(l)


state = 0
cur = None

for line in sys.stdin:
    if state == 0:
        if line.strip().startswith("(footprint"):
            # Make a new footprint starting with this line...
            cur = Footprint(line)
            
            # ...then go to state 1.
            state = 1
            continue

        # Nothing special. Dump the line.
        sys.stdout.write(line)
        continue

    elif state == 1:
        if not line.strip():
            # print(cur)
            cur.rectify()
            cur.dump()
            cur = None
            state = 0

        m = reAt.match(line.strip())

        if m:
            cur.locate(line, m.groups())
            continue

        m = reText.match(line.strip())

        if m:
            cur.addText(line, m.groups())
            continue

        if cur:
            cur.addLine(line)
        else:
            sys.stdout.write(line)
