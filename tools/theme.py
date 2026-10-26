#!/usr/bin/env python3
import os
import sys

INK = "#2e2a26"
SURFACE = "#faf8f5"
CARD = "#ffffff"
LINE = "rgba(46,42,38,0.12)"
ACCENT = "#607296"
SHADOW = (60, 44, 30)
GAP = 16

SIDES = ("top", "bottom", "left", "right")
CORNERS = ("topleft", "topright", "bottomleft", "bottomright")


def paint(value, kind):
    if value.startswith("rgba("):
        r, g, b, a = value[5:-1].split(",")
        return f'{kind}="rgb({r},{g},{b})" {kind}-opacity="{a}"'
    return f'{kind}="{value}"'


class Sheet:
    def __init__(self, interior="center"):
        self.interior = interior
        self.parts = []
        self.defs = []
        self.y = 0

    def group(self, name, x, y, w, h, body=""):
        if not body:
            body = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000" fill-opacity="0"/>'
        self.parts.append(f'<g id="{name}">{body}</g>')

    def gradient(self, name, kind, stops, **attrs):
        tag = "radialGradient" if kind == "radial" else "linearGradient"
        a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        s = "".join(
            f'<stop offset="{o}" stop-color="rgb{SHADOW}" stop-opacity="{op}"/>' for o, op in stops
        )
        self.defs.append(f'<{tag} id="{name}" gradientUnits="userSpaceOnUse" {a}>{s}</{tag}>')
        return f"url(#{name})"

    def frame(self, prefix, r, fill, stroke=None, sides=SIDES, edge=None, hints=None):
        name = (prefix + "-") if prefix else ""
        x0, y0 = 0, self.y
        f = paint(fill, "fill")
        s = paint(stroke, "fill") if stroke else None
        m = r if edge is None else edge
        for i, c in enumerate(CORNERS):
            x, y = x0 + i * (m + GAP), y0
            cx = x + (m if "left" in c else 0)
            cy = y + (m if c.startswith("top") else 0)
            vertical = "top" if c.startswith("top") else "bottom"
            horizontal = "left" if "left" in c else "right"
            if vertical in sides and horizontal in sides and r > 0:
                sx = cx - r if horizontal == "left" else cx + r
                sy = cy - r if vertical == "top" else cy + r
                sweep = 1 if (horizontal == "left") == (vertical == "top") else 0
                body = f'<path d="M{cx} {cy}L{sx} {cy}A{r} {r} 0 0 {sweep} {cx} {sy}Z" {f}/>'
                if s:
                    h = 1 if horizontal == "left" else -1
                    v = 1 if vertical == "top" else -1
                    body += f'<path d="M{sx} {cy}A{r} {r} 0 0 {sweep} {cx} {sy}V{sy + v}A{r - 1} {r - 1} 0 0 {1 - sweep} {sx + h} {cy}Z" {s}/>'
            else:
                body = f'<rect x="{x}" y="{y}" width="{m}" height="{m}" {f}/>'
                if s:
                    if vertical in sides:
                        ly = y if vertical == "top" else y + m - 1
                        body += f'<rect x="{x}" y="{ly}" width="{m}" height="1" {s}/>'
                    if horizontal in sides:
                        lx = x if horizontal == "left" else x + m - 1
                        body += f'<rect x="{lx}" y="{y}" width="1" height="{m}" {s}/>'
            self.group(name + c, x, y, m, m, body)
        bx = x0 + 4 * (m + GAP)
        for i, side in enumerate(SIDES):
            x, y = bx + i * (m + GAP), y0
            body = f'<rect x="{x}" y="{y}" width="{m}" height="{m}" {f}/>'
            if s and side in sides:
                lx, ly, lw, lh = {
                    "top": (x, y, m, 1),
                    "bottom": (x, y + m - 1, m, 1),
                    "left": (x, y, 1, m),
                    "right": (x + m - 1, y, 1, m),
                }[side]
                body += f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" {s}/>'
            self.group(name + side, x, y, m, m, body)
        cx = bx + 4 * (m + GAP)
        self.group(name + self.interior if self.interior else name.rstrip("-"), cx, y0, m, m, f'<rect x="{cx}" y="{y0}" width="{m}" height="{m}" {f}/>')
        hx = cx + m + GAP
        for i, (side, size) in enumerate((hints or {}).items()):
            w, h = (size, 1) if side in ("left", "right") else (1, size)
            self.group(f"{name}hint-{side}-margin", hx + i * 40, y0, max(w, 1), max(h, 1))
        self.y += m + GAP

    def shadow(self, prefix, size, strength, inset=0):
        name = (prefix + "-") if prefix else ""
        y0 = self.y
        stops = [(0, strength), (0.35, strength * 0.45), (1, 0)]
        for i, c in enumerate(CORNERS):
            x = i * (size + GAP)
            cx = x + (size if "left" in c else 0)
            cy = y0 + (size if c.startswith("top") else 0)
            g = self.gradient(f"{name}sh-{c}", "radial", stops, cx=cx, cy=cy, r=size)
            self.group(f"{name}shadow-{c}", x, y0, size, size, f'<rect x="{x}" y="{y0}" width="{size}" height="{size}" fill="{g}"/>')
        bx = 4 * (size + GAP)
        for i, side in enumerate(SIDES):
            x = bx + i * (size + GAP)
            ends = {
                "top": (x, y0 + size, x, y0),
                "bottom": (x, y0, x, y0 + size),
                "left": (x + size, y0, x, y0),
                "right": (x, y0, x + size, y0),
            }[side]
            g = self.gradient(f"{name}sh-{side}", "linear", stops, x1=ends[0], y1=ends[1], x2=ends[2], y2=ends[3])
            self.group(f"{name}shadow-{side}", x, y0, size, size, f'<rect x="{x}" y="{y0}" width="{size}" height="{size}" fill="{g}"/>')
        for i, side in enumerate(SIDES):
            self.group(f"{name}shadow-hint-{side}-margin", bx + (4 + i) * (size + GAP), y0, inset or 1, inset or 1)
        self.y += size + GAP

    def raw(self, name, x, y, w, h, body):
        self.group(name, x, y, w, h, body)

    def write(self, path, flags=()):
        for flag in flags:
            self.group(flag, 0, self.y, 1, 1)
            self.y += 2
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as out:
            out.write('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="%d">' % (self.y + 4))
            out.write("<defs>" + "".join(self.defs) + "</defs>")
            out.write("".join(self.parts))
            out.write("</svg>\n")


def plasma(root):
    base = os.path.join(root, "usr/share/plasma/desktoptheme/org.avenor.desktop")

    def card(r, fill, hints, shadow, strength):
        s = Sheet()
        s.frame("", r, fill, LINE, hints=hints)
        s.frame("mask", r, SURFACE)
        s.shadow("", shadow, strength)
        return s

    pad = {"top": 3, "bottom": 3, "left": 12, "right": 12}
    for folder, alpha in (("", 0.86), ("translucent/", 0.86), ("solid/", 1)):
        card(14, f"rgba(250,248,245,{alpha})", pad, 18, 0.16).write(
            f"{base}/{folder}widgets/panel-background.svg", ["hint-stretch-borders"]
        )
        card(16, SURFACE, {"top": 12, "bottom": 12, "left": 12, "right": 12}, 28, 0.18).write(
            f"{base}/{folder}dialogs/background.svg", ["hint-stretch-borders"]
        )
        card(10, SURFACE, {"top": 6, "bottom": 6, "left": 10, "right": 10}, 14, 0.14).write(
            f"{base}/{folder}widgets/tooltip.svg", ["hint-stretch-borders"]
        )

    s = Sheet()
    s.frame("", 16, SURFACE, LINE)
    s.shadow("", 20, 0.12)
    s.write(f"{base}/widgets/background.svg", ["hint-stretch-borders"])

    s = Sheet()
    s.frame("normal", 8, CARD, LINE)
    s.frame("hover", 8, "#f4f0ea", "rgba(46,42,38,0.18)")
    s.frame("focus", 8, CARD, "rgba(96,114,150,0.6)")
    s.frame("pressed", 8, "#ece6de", "rgba(46,42,38,0.18)")
    s.frame("toolbutton-hover", 8, "rgba(46,42,38,0.06)")
    s.frame("toolbutton-focus", 8, "rgba(46,42,38,0.06)", "rgba(96,114,150,0.5)")
    s.frame("toolbutton-pressed", 8, "rgba(46,42,38,0.10)")
    s.write(f"{base}/widgets/button.svg", ["hint-stretch-borders"])

    s = Sheet()
    s.frame("base", 10, "#f3efe9", "rgba(46,42,38,0.10)")
    s.frame("hover", 10, "#f3efe9", "rgba(46,42,38,0.18)")
    s.frame("focus", 10, CARD, "rgba(96,114,150,0.55)")
    s.write(f"{base}/widgets/lineedit.svg", ["hint-stretch-borders"])

    s = Sheet()
    s.frame("normal", 10, "rgba(46,42,38,0.05)")
    s.frame("hover", 10, "rgba(46,42,38,0.08)")
    s.frame("focus", 10, "rgba(46,42,38,0.12)")
    s.frame("attention", 10, "rgba(176,132,84,0.22)")
    s.frame("minimized", 10, "rgba(46,42,38,0.03)")
    s.frame("progress", 10, "rgba(96,114,150,0.22)")
    s.write(f"{base}/widgets/tasks.svg", ["hint-stretch-borders"])

    s = Sheet()
    s.frame("normal", 8, "rgba(0,0,0,0)")
    s.frame("hover", 8, "rgba(46,42,38,0.06)")
    s.frame("selected", 8, "rgba(96,114,150,0.14)")
    s.frame("selected+hover", 8, "rgba(96,114,150,0.20)")
    s.write(f"{base}/widgets/viewitem.svg", ["hint-stretch-borders"])

    s = Sheet()
    s.frame("header", 4, "rgba(0,0,0,0)", LINE, sides=("bottom",))
    s.frame("footer", 4, "rgba(0,0,0,0)", LINE, sides=("top",))
    s.write(f"{base}/widgets/plasmoidheading.svg", ["hint-stretch-borders"])

    with open(f"{base}/metadata.json", "w") as out:
        out.write(
            '{\n    "KPackageStructure": "Plasma/Theme",\n    "KPlugin": {\n'
            '        "Authors": [{ "Name": "AvenorOS" }],\n'
            '        "Description": "Warm, quiet surfaces for AvenorOS",\n'
            '        "Id": "org.avenor.desktop",\n        "License": "GPL-3.0-or-later",\n'
            '        "Name": "Avenor",\n        "Version": "0.3.0"\n    },\n'
            '    "X-Plasma-API": "5.0"\n}\n'
        )


def glyph(kind, x, y):
    c = 8
    p = {
        "close": f"M{x + c - 3} {y + c - 3}l6 6M{x + c + 3} {y + c - 3}l-6 6",
        "minimize": f"M{x + c - 3.5} {y + c}h7",
        "maximize": f"M{x + c - 3} {y + c + 2}l3 -3 3 3",
        "restore": f"M{x + c - 3} {y + c - 1}l3 3 3 -3",
    }[kind]
    return f'<path d="{p}" fill="none" stroke="{INK}" stroke-opacity="0.75" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'


def aurorae(root):
    base = os.path.join(root, "usr/share/aurorae/themes/Avenor")
    s = Sheet()
    s.frame("decoration", 10, SURFACE, LINE)
    s.frame("decoration-inactive", 10, SURFACE, "rgba(46,42,38,0.08)")
    for prefix in ("decoration-maximized", "decoration-maximized-inactive"):
        s.frame(prefix, 0, SURFACE, edge=4)
    s.write(f"{base}/decoration.svg")

    for kind in ("close", "minimize", "maximize", "restore"):
        b = Sheet()
        states = {
            "active": (5, 0.16, False),
            "inactive": (5, 0.08, False),
            "hover": (8, 0.10, True),
            "pressed": (8, 0.18, True),
            "deactivated": (5, 0.05, False),
        }
        for i, (state, (radius, alpha, mark)) in enumerate(states.items()):
            x = i * 20
            body = f'<rect x="{x}" y="0" width="16" height="16" fill="none"/><circle cx="{x + 8}" cy="8" r="{radius}" fill="rgb(46,42,38)" fill-opacity="{alpha}"/>'
            if mark:
                body += glyph(kind, x, 0)
            b.raw(f"{state}-center", x, 0, 16, 16, body)
        b.y = 18
        b.write(f"{base}/{kind}.svg")


def kvantum(root):
    base = os.path.join(root, "usr/share/Kvantum/Avenor")
    s = Sheet(interior="")

    def states(element, r, table):
        for state, (fill, stroke) in table.items():
            s.frame(f"{element}-{state}", r, fill, stroke)

    states("button", 8, {
        "normal": (CARD, LINE),
        "focused": ("#f6f2ec", "rgba(46,42,38,0.20)"),
        "pressed": ("#ece6de", "rgba(46,42,38,0.20)"),
        "toggled": ("#e9edf4", "rgba(96,114,150,0.45)"),
        "disabled": ("#f5f2ee", "rgba(46,42,38,0.08)"),
    })
    states("tbutton", 8, {
        "normal": ("rgba(0,0,0,0)", None),
        "focused": ("rgba(46,42,38,0.06)", None),
        "pressed": ("rgba(46,42,38,0.10)", None),
        "toggled": ("rgba(96,114,150,0.14)", None),
        "disabled": ("rgba(0,0,0,0)", None),
    })
    states("lineedit", 8, {
        "normal": ("#f3efe9", "rgba(46,42,38,0.10)"),
        "focused": (CARD, "rgba(96,114,150,0.55)"),
        "disabled": ("#f5f2ee", "rgba(46,42,38,0.06)"),
    })
    states("common", 12, {"normal": (CARD, LINE), "disabled": (CARD, LINE)})
    states("group", 12, {"normal": (CARD, LINE)})
    states("tabframe", 12, {"normal": (CARD, LINE)})
    states("menu", 12, {"normal": (SURFACE, "rgba(46,42,38,0.14)")})
    states("tooltip", 10, {"normal": (SURFACE, "rgba(46,42,38,0.14)")})
    states("menuitem", 6, {
        "normal": ("rgba(0,0,0,0)", None),
        "focused": ("rgba(46,42,38,0.07)", None),
        "pressed": ("rgba(46,42,38,0.10)", None),
        "toggled": ("rgba(46,42,38,0.07)", None),
    })
    states("menubaritem", 6, {
        "normal": ("rgba(0,0,0,0)", None),
        "focused": ("rgba(46,42,38,0.06)", None),
        "pressed": ("rgba(46,42,38,0.10)", None),
        "toggled": ("rgba(46,42,38,0.08)", None),
    })
    states("itemview", 8, {
        "normal": ("rgba(0,0,0,0)", None),
        "focused": ("rgba(46,42,38,0.05)", None),
        "pressed": ("rgba(96,114,150,0.16)", None),
        "toggled": ("rgba(96,114,150,0.16)", None),
    })
    states("tab", 8, {
        "normal": ("rgba(0,0,0,0)", None),
        "focused": ("rgba(46,42,38,0.05)", None),
        "toggled": (CARD, LINE),
        "pressed": ("rgba(46,42,38,0.08)", None),
    })
    states("scrollbarslider", 4, {
        "normal": ("rgba(46,42,38,0.22)", None),
        "focused": ("rgba(46,42,38,0.36)", None),
        "pressed": ("rgba(46,42,38,0.46)", None),
        "disabled": ("rgba(46,42,38,0.10)", None),
    })
    states("slider", 3, {
        "normal": ("rgba(46,42,38,0.12)", None),
        "toggled": (ACCENT, None),
        "focused": ("rgba(46,42,38,0.16)", None),
        "disabled": ("rgba(46,42,38,0.06)", None),
    })
    states("progress", 4, {"normal": ("rgba(46,42,38,0.10)", None)})
    states("progress-pattern", 4, {"normal": (ACCENT, None)})
    states("header", 1, {
        "normal": (SURFACE, LINE),
        "focused": ("#f4f0ea", LINE),
        "pressed": ("#ece6de", LINE),
        "toggled": (SURFACE, LINE),
    })

    x = 0
    y = s.y
    for state, alpha in (("normal", 0.7), ("focused", 0.9), ("pressed", 0.9), ("toggled", 0.9), ("disabled", 0.3)):
        for direction, d in (
            ("down", "M4 6.5l4 4 4-4"),
            ("up", "M4 10l4-4 4 4"),
            ("left", "M10 4l-4 4 4 4"),
            ("right", "M6.5 4l4 4-4 4"),
        ):
            body = f'<g transform="translate({x} {y})"><path d="{d}" fill="none" stroke="{INK}" stroke-opacity="{alpha}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></g>'
            s.raw(f"arrow-{direction}-{state}", x, y, 16, 16, body)
            x += 18
    y += 20
    x = 0
    for state, ring in (("normal", 0.28), ("focused", 0.45), ("pressed", 0.45), ("disabled", 0.12)):
        for checked in (False, True):
            name = f"checkbox-checked-{state}" if checked else f"checkbox-{state}"
            fill = ACCENT if checked else CARD
            body = f'<rect x="{x + 1.5}" y="{y + 1.5}" width="15" height="15" rx="4.5" fill="{fill}" stroke="{INK if not checked else ACCENT}" stroke-opacity="{ring if not checked else 1}"/>'
            if checked:
                body += f'<path d="M{x + 5} {y + 9.2}l2.8 2.8 5.2-5.6" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
            s.raw(name, x, y, 18, 18, body)
            x += 20
            name = f"radio-checked-{state}" if checked else f"radio-{state}"
            body = f'<circle cx="{x + 9}" cy="{y + 9}" r="7.5" fill="{fill}" stroke="{INK if not checked else ACCENT}" stroke-opacity="{ring if not checked else 1}"/>'
            if checked:
                body += f'<circle cx="{x + 9}" cy="{y + 9}" r="3" fill="#fff"/>'
            s.raw(name, x, y, 18, 18, body)
            x += 20
    y += 22
    for i, state in enumerate(("normal", "focused", "pressed", "disabled")):
        x = i * 22
        alpha = 0.18 if state != "disabled" else 0.08
        body = f'<circle cx="{x + 10}" cy="{y + 10}" r="8.5" fill="{CARD}" stroke="{INK}" stroke-opacity="{alpha}"/>'
        s.raw(f"slidercursor-{state}", x, y, 20, 20, body)
    s.y = y + 24
    s.write(f"{base}/Avenor.svg")


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "mkosi.extra"
    plasma(root)
    aurorae(root)
    kvantum(root)
