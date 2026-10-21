"""Build the VectorCraft UI proposal in FigCraft over its control channel.

Pages: Rationale, Current (0.13), Proposal A (Flat), Proposal B (Quiet), Overview.
Every screen is 1440 x 900 and shares one layout; the themes only change tokens.
"""
import base64, json, os, re, sys
from fc import FC

ICONS = "/tmp/vectorcraft/assets/icons"
OUT = "/tmp/vcdesign"
W, H = 1440, 900

f = FC(int(os.environ.get("FC_PORT", "7981")))


# ---------------------------------------------------------------- primitives
def props_of(fill=None, r=None, fx=None, stroke=None, sw=1.0, **extra):
    p = {"fills": [fill] if isinstance(fill, str) else (fill or [])}
    if r is not None:
        p["cornerRadius"] = r
    if fx:
        p["effects"] = fx
    if stroke:
        p["strokes"] = [stroke]
        p["strokeWeight"] = sw
        p["strokeAlign"] = "inside"
    p.update({k: v for k, v in extra.items() if v is not None})
    return p


def fr(parent, x, y, w, h, name, fill=None, r=None, fx=None, stroke=None, sw=1.0, **layout):
    p = props_of(fill, r, fx, stroke, sw, **layout)
    args = dict(type="frame", x=x, y=y, width=w, height=h, name=name, props=p, select=False)
    if parent is not None:
        args["parent"] = parent
    return f.run("node.create", **args)["id"]


def rc(parent, x, y, w, h, fill=None, r=None, fx=None, stroke=None, sw=1.0, name="Rectangle", **extra):
    p = props_of(fill, r, fx, stroke, sw, **extra)
    return f.run("node.create", type="rectangle", parent=parent, x=x, y=y, width=w, height=h, name=name, props=p, select=False)["id"]


def el(parent, x, y, w, h, fill=None, stroke=None, sw=1.0, name="Ellipse"):
    p = props_of(fill, None, None, stroke, sw)
    return f.run("node.create", type="ellipse", parent=parent, x=x, y=y, width=w, height=h, name=name, props=p, select=False)["id"]


def tx(parent, s, x, y, size, color, style="Regular", w=None, align=None, name=None, **extra):
    p = {"fontFamily": "Inter", "fontStyle": style, "fontSize": size, "fills": [color]}
    if align:
        p["textAlign"] = align
    p.update(extra)
    args = dict(text=s, x=x, y=y, parent=parent, props=p)
    if w:
        args["width"] = w
    i = f.run("text.create", **args)["id"]
    if name:
        f.run("node.set", ids=[i], props={"name": name})
    return i


def line_h(size):
    return round(size * 1.21)


_svg_cache = {}


def ic(parent, name, x, y, size, color):
    """One of VectorCraft's own icons (assets/icons, MIT/Apache or Lucide ISC), recoloured."""
    key = (name, size, color)
    if key not in _svg_cache:
        svg = open(f"{ICONS}/{name}.svg").read()
        svg = svg.replace("currentColor", color)
        svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
        svg = re.sub(r'\bwidth="24"', f'width="{size}"', svg, count=1)
        svg = re.sub(r'\bheight="24"', f'height="{size}"', svg, count=1)
        sw = round(1.45 * 24 / size, 3)
        svg = re.sub(r'stroke-width="(1\.5|2)"', f'stroke-width="{sw}"', svg)
        _svg_cache[key] = base64.b64encode(svg.encode()).decode()
    i = f.run("file.import", data=_svg_cache[key], name=f"{name}.svg", x=-5000, y=-5000)["id"]
    f.run("node.reparent", ids=[i], parent=parent)
    f.run("node.set", ids=[i], props={"x": x, "y": y, "name": f"icon/{name}"})
    return i


def interact(node, dest):
    f.run("proto.interaction.add", id=node, trigger={"type": "onClick"}, action={"type": "navigate", "dest": dest, "transition": {"type": "dissolve", "durationMs": 120}})


# ---------------------------------------------------------------- themes
SHADOW = lambda c, y, blur, spread=0: {"type": "dropShadow", "color": c, "offset": [0, y], "radius": blur, "spread": spread}
INNER = lambda c, y, blur: {"type": "innerShadow", "color": c, "offset": [0, y], "radius": blur, "spread": 0}

FLAT = dict(
    key="A", name="Flat Dark", dark=True,
    appbar_h=40, status_h=28, tool_w=64, tool_btn=28, tool_step=30, tool_cols=(4, 32), tool_icon=18,
    rail_w=40, rail_btn=28, rail_step=32, dock_w=288, ctrl_h=28, row_h=32,
    chrome="#1F2023", appbar="#1A1B1E", divider="#2E3035", pasteboard="#2A2B2F",
    text1="#E4E5E8", text2="#9EA2AA", text3="#6C7079", icon="#AEB2B9",
    field="#28292D", field_fx=None, raised="#2D2E33", raised_fx=None, button_stroke=None,
    accent="#5B8DEF", accent_soft="#5B8DEF2E", tool_active="#3A3C42", tool_active_fx=None, icon_active="#FFFFFF",
    float_fill="#26272B", float_fx=[SHADOW("#00000073", 8, 24)], float_stroke="#34363B",
    r_ctrl=4, r_float=8, r_tab=0, r_swatch=2, r_handle=0,
    lines=True, tabs="underline",
    artboard_fx=[SHADOW("#00000059", 2, 8)],
)

FLAT_LIGHT = dict(FLAT, name="Flat Light", dark=False,
    chrome="#F5F5F6", appbar="#EDEEF0", divider="#DCDEE2", pasteboard="#E4E5E8",
    text1="#1E2025", text2="#5E636B", text3="#8E939B", icon="#4E535B",
    field="#EAEBED", raised="#E4E5E8", accent="#2F6BE0", accent_soft="#2F6BE01F",
    tool_active="#DCDEE2", icon_active="#111317",
    float_fill="#FFFFFF", float_fx=[SHADOW("#0000001F", 8, 24)], float_stroke="#DCDEE2",
    artboard_fx=[SHADOW("#00000024", 2, 8)],
)

QUIET_LIGHT = dict(
    key="B", name="Quiet Light", dark=False,
    appbar_h=44, status_h=30, tool_w=80, tool_btn=32, tool_step=36, tool_cols=(7, 41), tool_icon=20,
    rail_w=48, rail_btn=32, rail_step=36, dock_w=296, ctrl_h=30, row_h=34,
    chrome="#F3F4F6", appbar="#F3F4F6", divider="#E3E5E9", pasteboard="#E7E9EC",
    text1="#1F2328", text2="#646A73", text3="#969CA5", icon="#545961",
    field="#E9EBEE", field_fx=[INNER("#00000012", 1, 2)], raised="#FFFFFF", raised_fx=[SHADOW("#0000001F", 1, 3)], button_stroke=None,
    accent="#3D6FE0", accent_soft="#3D6FE01F", tool_active="#FFFFFF", tool_active_fx=[SHADOW("#00000024", 1, 4)], icon_active="#1F2328",
    float_fill="#FFFFFF", float_fx=[SHADOW("#0000001A", 8, 28), SHADOW("#00000014", 1, 3)], float_stroke=None,
    r_ctrl=8, r_float=14, r_tab=999, r_swatch=6, r_handle=2,
    lines=False, tabs="segmented",
    artboard_fx=[SHADOW("#0000001A", 4, 18), SHADOW("#0000000F", 1, 2)],
)

QUIET_DARK = dict(QUIET_LIGHT, name="Quiet Dark", dark=True,
    chrome="#1D1E21", appbar="#1D1E21", divider="#2B2D31", pasteboard="#2A2C30",
    text1="#E7E8EA", text2="#A0A4AB", text3="#6F737B", icon="#B9BCC2",
    field="#16171A", field_fx=[INNER("#00000066", 1, 2)], raised="#2C2E33", raised_fx=[SHADOW("#00000080", 1, 3)],
    accent="#6E97F2", accent_soft="#6E97F22E", tool_active="#34363C", tool_active_fx=[SHADOW("#00000080", 1, 4)], icon_active="#FFFFFF",
    float_fill="#2A2C30", float_fx=[SHADOW("#00000080", 8, 28)], float_stroke="#34363B",
    artboard_fx=[SHADOW("#00000066", 4, 18)],
)

# The art is the only colourful thing on screen.
ART = dict(circle="#F2B134", rect="#2A6F97", text="#1B1B1B")

TOOLS = ["dc-selection", "dc-direct", "wand-sparkles", "lasso", "pen-tool", "spline", "type", "dc-line",
         "square", "dc-ellipse", "hexagon", "star", "paintbrush", "pencil", "eraser", "scissors",
         "rotate-ccw", "scaling", "dc-width", "dc-free-transform", "dc-shape-builder", "dc-perspective",
         "dc-mesh", "dc-gradient", "pipette", "dc-measure", "dc-artboards", "slice", "hand", "zoom-in"]
RAIL = [["palette", "swatch-book", "paintbrush", "dc-symbol-sprayer"], ["dc-stroke", "dc-gradient", "dc-transparency"],
        ["dc-appearance", "dc-graphic-styles"], ["dc-align", "dc-transform-panel", "dc-pathfinder"],
        ["type", "pilcrow"], ["history", "dc-actions", "info", "chart-column"]]


# ---------------------------------------------------------------- components drawn per theme
def field(t, parent, x, y, w, label, value, unit=""):
    i = fr(parent, x, y, w, t["ctrl_h"], f"field/{label or value}", t["field"], t["r_ctrl"], t["field_fx"],
           layout="horizontal", padding=[0, 8, 0, 8], gap=6, crossAlign="center")
    if label:
        tx(i, label, 0, 0, 11, t["text3"], "SemiBold")
    tx(i, value + unit, 0, 0, 12, t["text1"])
    return i


def button(t, parent, x, y, w, label, primary=False, icon=None):
    fill = t["accent"] if primary else t["raised"]
    fx = None if primary else t["raised_fx"]
    i = fr(parent, x, y, w, t["ctrl_h"], f"button/{label}", fill, t["r_ctrl"], fx,
           layout="horizontal", mainAlign="center", crossAlign="center", gap=6)
    if icon:
        ic(i, icon, 0, 0, 16, "#FFFFFF" if primary else t["icon"])
    tx(i, label, 0, 0, 12, "#FFFFFF" if primary else t["text1"], "SemiBold" if primary else "Regular")
    return i


def icon_button(t, parent, x, y, size, icon, isize, active=False, color=None):
    fill = t["tool_active"] if active else None
    fx = t["tool_active_fx"] if active else None
    i = fr(parent, x, y, size, size, f"button/{icon}", fill, t["r_ctrl"], fx)
    ic(i, icon, (size - isize) / 2, (size - isize) / 2, isize, color or (t["icon_active"] if active else t["icon"]))
    return i


def divider(t, parent, x, y, w, h):
    return rc(parent, x, y, w, h, t["divider"], name="divider")


def section_title(t, parent, x, y, s):
    return tx(parent, s, x, y, 12, t["text1"], "SemiBold", name=f"title/{s}")


# ---------------------------------------------------------------- the screen
def screen(t, tab, px, py):
    """One 1440 x 900 window. Returns (frame, hotspots)."""
    hot = {}
    root = fr(None, px, py, W, H, f"{t['key']} · {t['name']} · {tab.title()}", t["chrome"], None, clip=True)
    ah, sh = t["appbar_h"], t["status_h"]
    dock_x = W - t["dock_w"]
    rail_x = dock_x - t["rail_w"]
    tool_w = t["tool_w"]

    # App bar: one row, the window's buttons, the file, search and workspace. No coloured buttons.
    bar = fr(root, 0, 0, W, ah, "App bar", t["appbar"])
    for k, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        el(bar, 14 + k * 20, ah / 2 - 6, 12, 12, c, name="window button")
    logo = f.run("image.place", path="/tmp/vectorcraft/assets/app-icon/vectorcraft-macos-512.png", x=0, y=0, width=20, height=20, parent=bar)["id"]
    f.run("node.set", ids=[logo], props={"x": 84, "y": ah / 2 - 10, "name": "VectorCraft"})
    icon_button(t, bar, 112, (ah - 28) / 2, 28, "house", 16)
    tx(bar, "Poster.vectorcraft", W / 2 - 60, ah / 2 - 8, 13, t["text2"], "SemiBold", w=120, align="center", name="title")
    rx = W - 16 - 132
    ws = fr(bar, rx, (ah - t["ctrl_h"]) / 2, 132, t["ctrl_h"], "Workspace", t["field"], t["r_ctrl"], t["field_fx"],
            layout="horizontal", padding=[0, 6, 0, 10], mainAlign="spaceBetween", crossAlign="center")
    tx(ws, "Essentials", 0, 0, 12, t["text1"])
    ic(ws, "chevron-down", 0, 0, 14, t["text2"])
    icon_button(t, bar, rx - 36, (ah - 28) / 2, 28, "search", 16)
    icon_button(t, bar, rx - 68, (ah - 28) / 2, 28, "message-circle", 16)
    hot["theme"] = icon_button(t, bar, rx - 100, (ah - 28) / 2, 28, "sun", 16)
    divider(t, root, 0, ah - 1, W, 1) if t["lines"] else None

    # Toolbar: flush to the window's edge, no card.
    tb = fr(root, 0, ah, tool_w, H - ah - sh, "Toolbar", t["chrome"])
    if t["lines"]:
        divider(t, tb, tool_w - 1, 0, 1, H - ah - sh)
    y = 10
    for k, name in enumerate(TOOLS):
        col = t["tool_cols"][k % 2]
        icon_button(t, tb, col, y, t["tool_btn"], name, t["tool_icon"], active=(k == 0))
        if k % 2:
            y += t["tool_step"]
    y += 14
    # Fill and stroke: the selected ellipse's paint.
    cx = tool_w / 2 - 17
    rc(tb, cx + 12, y + 12, 22, 22, None, t["r_swatch"], stroke=t["text1"], sw=3, name="stroke")
    rc(tb, cx, y, 22, 22, ART["circle"], t["r_swatch"], stroke=t["chrome"], sw=1.5, name="fill")
    y += 46
    icon_button(t, tb, (tool_w - 28) / 2, y, 28, "ellipsis", 16)

    # Canvas column: document tabs, pasteboard, artboard.
    cw = rail_x - tool_w
    tabs_h = 34
    doc = fr(root, tool_w, ah, cw, tabs_h, "Document tabs", t["chrome"])
    if t["lines"]:
        dtab = fr(doc, 0, 0, 220, tabs_h, "tab/Poster", t["pasteboard"], 0, layout="horizontal", padding=[0, 10, 0, 12], gap=8,
                  crossAlign="center", mainAlign="spaceBetween")
        divider(t, doc, 220, 0, 1, tabs_h)
        divider(t, doc, 221, tabs_h - 1, cw - 221, 1)
    else:
        dtab = fr(doc, 8, 4, 220, tabs_h - 8, "tab/Poster", t["raised"], t["r_ctrl"], t["raised_fx"], layout="horizontal",
                  padding=[0, 8, 0, 12], gap=8, crossAlign="center", mainAlign="spaceBetween")
    tx(dtab, "Poster.vectorcraft  ·  95%", 0, 0, 12, t["text1"])
    ic(dtab, "x", 0, 0, 14, t["text3"])

    pb_y = ah + tabs_h
    pb_h = H - sh - pb_y
    pb = fr(root, tool_w, pb_y, cw, pb_h, "Canvas", t["pasteboard"], clip=True)
    s = 0.95
    abw, abh = 800 * s, 600 * s
    ax, ay = (cw - abw) / 2, (pb_h - abh) / 2 - 6
    tx(pb, "Artboard 1", ax, ay - 20, 11, t["text3"], name="artboard name")
    ab = fr(pb, ax, ay, abw, abh, "Artboard 1", "#FFFFFF", 0, t["artboard_fx"], clip=True)
    circ = (120 * s, 150 * s, 260 * s)
    el(ab, circ[0], circ[1], circ[2], circ[2], ART["circle"], name="Ellipse")
    rc(ab, 420 * s, 210 * s, 240 * s, 200 * s, ART["rect"], 0, name="Rectangle")
    tx(ab, "Poster draft", 120 * s, 482 * s, 46, ART["text"], "SemiBold", name="Poster draft")
    # Selection on the ellipse, in the one accent colour.
    bx, by, bw = ax + circ[0], ay + circ[1], circ[2]
    rc(pb, bx, by, bw, bw, None, 0, stroke=t["accent"], sw=1, name="selection")
    for hx in (0, 0.5, 1):
        for hy in (0, 0.5, 1):
            if hx == 0.5 and hy == 0.5:
                continue
            rc(pb, bx + hx * bw - 3.5, by + hy * bw - 3.5, 7, 7, "#FFFFFF", t["r_handle"], stroke=t["accent"], sw=1, name="handle")
    rc(pb, bx + bw / 2 - 2, by + bw / 2 - 2, 4, 4, t["accent"], 0, name="centre")
    # The contextual task bar floats, so it is the one panel with a shadow and larger corners.
    task = fr(pb, bx - 2, by + bw + 14, 10, 40, "Contextual task bar", t["float_fill"], t["r_float"], t["float_fx"],
              stroke=t["float_stroke"], layout="horizontal", padding=[0, 6, 0, 6], gap=2, crossAlign="center", sizingH="hug")
    for icon, label in [("pen-tool", "Edit Path"), ("square-dashed", "Offset Path"), ("spline", "Simplify"), ("copy", "Duplicate")]:
        b = fr(task, 0, 0, 10, 28, f"task/{label}", None, t["r_ctrl"], layout="horizontal", padding=[0, 8, 0, 8], gap=6,
               crossAlign="center", sizingH="hug")
        ic(b, icon, 0, 0, 16, t["icon"])
        tx(b, label, 0, 0, 12, t["text1"])
    rc(task, 0, 0, 1, 18, t["divider"], name="divider")
    sw_ = fr(task, 0, 0, 28, 28, "task/fill", None, t["r_ctrl"], layout="horizontal", mainAlign="center", crossAlign="center")
    rc(sw_, 0, 0, 16, 16, ART["circle"], t["r_swatch"], name="swatch")
    icon_button(t, task, 0, 0, 28, "lock", 16)
    icon_button(t, task, 0, 0, 28, "ellipsis", 16)

    # Icon rail: same surface as the dock.
    rail = fr(root, rail_x, ah, t["rail_w"], H - ah - sh, "Panel rail", t["chrome"])
    if t["lines"]:
        divider(t, rail, 0, 0, 1, H - ah - sh)
        divider(t, rail, t["rail_w"] - 1, 0, 1, H - ah - sh)
    y = 10
    for gi, group in enumerate(RAIL):
        for name in group:
            icon_button(t, rail, (t["rail_w"] - t["rail_btn"]) / 2, y, t["rail_btn"], name, 18 if t["key"] == "A" else 20)
            y += t["rail_step"]
        if gi < len(RAIL) - 1:
            if t["lines"]:
                divider(t, rail, 10, y + 3, t["rail_w"] - 20, 1)
            y += 8

    # Dock: flush, one surface, tabs at the top.
    dw = t["dock_w"]
    dock = fr(root, dock_x, ah, dw, H - ah - sh, "Panel dock", t["chrome"], clip=True)
    names = ["Properties", "Layers", "Libraries"]
    if t["tabs"] == "underline":
        th = 36
        x = 14
        for n in names:
            on = n.lower() == tab
            tid = tx(dock, n, x, (th - line_h(12)) / 2, 12, t["text1"] if on else t["text2"], "SemiBold" if on else "Regular", name=f"tab/{n}")
            wdt = f.call("node.get", {"id": tid})["width"]
            if on:
                rc(dock, x, th - 2, wdt, 2, t["text1"], 0, name="tab indicator")
            hot[n.lower()] = tid
            x += wdt + 20
        icon_button(t, dock, dw - 36, (th - 28) / 2, 28, "menu", 16)
        divider(t, dock, 0, th - 1, dw, 1)
        cy = th + 14
    else:
        th = 52
        track = fr(dock, 14, 10, dw - 14 - 48, 32, "Panel tabs", t["field"], t["r_tab"], t["field_fx"],
                   layout="horizontal", padding=[3, 3, 3, 3], gap=2, crossAlign="center")
        for n in names:
            on = n.lower() == tab
            chip = fr(track, 0, 0, 10, 26, f"tab/{n}", t["raised"] if on else None, t["r_tab"], t["raised_fx"] if on else None,
                      layout="horizontal", mainAlign="center", crossAlign="center", sizingH="fill")
            tx(chip, n, 0, 0, 12, t["text1"] if on else t["text2"], "SemiBold" if on else "Regular")
            hot[n.lower()] = chip
        icon_button(t, dock, dw - 42, 12, 28, "menu", 16)
        cy = th + 12
    pad = 16
    inner = dw - 2 * pad
    gap_sec = 14 if t["lines"] else 22

    def sep(y):
        if t["lines"]:
            divider(t, dock, 0, y, dw, 1)
            return y + gap_sec
        return y + gap_sec

    if tab == "properties":
        tx(dock, "Ellipse", pad, cy, 11, t["text3"], name="selection kind")
        cy += 24
        section_title(t, dock, pad, cy, "Transform")
        cy += 24
        ic(dock, "dc-reference-point", pad, cy + (t["ctrl_h"] - 20) / 2, 20, t["icon"])
        fw = (inner - 32 - 8) / 2
        field(t, dock, pad + 32, cy, fw, "X", "250", " pt")
        field(t, dock, pad + 32 + fw + 8, cy, fw, "Y", "250", " pt")
        cy += t["ctrl_h"] + 8
        ic(dock, "link", pad + 2, cy + (t["ctrl_h"] - 16) / 2, 16, t["text3"])
        field(t, dock, pad + 32, cy, fw, "W", "260", " pt")
        field(t, dock, pad + 32 + fw + 8, cy, fw, "H", "260", " pt")
        cy += t["ctrl_h"] + 8
        field(t, dock, pad + 32, cy, fw, "∠", "0°")
        icon_button(t, dock, pad + 32 + fw + 8, cy, t["ctrl_h"], "flip-horizontal-2", 16)
        icon_button(t, dock, pad + 32 + fw + 8 + t["ctrl_h"] + 4, cy, t["ctrl_h"], "flip-vertical-2", 16)
        icon_button(t, dock, dw - pad - t["ctrl_h"], cy, t["ctrl_h"], "ellipsis", 16)
        cy += t["ctrl_h"] + 14
        cy = sep(cy)
        section_title(t, dock, pad, cy, "Appearance")
        icon_button(t, dock, dw - pad - 24, cy - 4, 24, "plus", 14)
        cy += 26
        for label, swatch, value in [("Fill", ART["circle"], "F2B134"), ("Stroke", None, "1 pt")]:
            row = fr(dock, pad, cy, inner, t["ctrl_h"], f"row/{label}", None, layout="horizontal", gap=8, crossAlign="center")
            sbox = fr(row, 0, 0, 22, 22, "swatch", swatch or t["field"], t["r_swatch"], None if swatch else t["field_fx"])
            if not swatch:
                ic(sbox, "dc-fill-none", 3, 3, 16, t["text3"])
            tx(row, label, 0, 0, 12, t["text1"])
            sp = fr(row, 0, 0, 10, 10, "spacer", None, sizingH="fill")
            fld = field(t, row, 0, 0, 104, None, value)
            ic(row, "eye", 0, 0, 16, t["text3"])
            cy += t["ctrl_h"] + 8
        row = fr(dock, pad, cy, inner, t["ctrl_h"], "row/Opacity", None, layout="horizontal", gap=8, crossAlign="center")
        tx(row, "Opacity", 0, 0, 12, t["text1"])
        fr(row, 0, 0, 10, 10, "spacer", None, sizingH="fill")
        field(t, row, 0, 0, 104, None, "100%")
        fr(row, 0, 0, 16, 16, "spacer", None)
        cy += t["ctrl_h"] + 8
        b = button(t, dock, pad, cy, 96, "Add effect", icon="dc-fx")
        cy += t["ctrl_h"] + 14
        cy = sep(cy)
        section_title(t, dock, pad, cy, "Align")
        cy += 26
        al = fr(dock, pad, cy, inner, t["ctrl_h"], "Align buttons", None, layout="horizontal", gap=4, crossAlign="center")
        for name in ["dc-al-left", "dc-al-hcenter", "dc-al-right", "dc-al-top", "dc-al-vcenter", "dc-al-bottom"]:
            icon_button(t, al, 0, 0, t["ctrl_h"], name, 18)
        fr(al, 0, 0, 10, 10, "spacer", None, sizingH="fill")
        icon_button(t, al, 0, 0, t["ctrl_h"], "ellipsis", 16)
        cy += t["ctrl_h"] + 14
        cy = sep(cy)
        section_title(t, dock, pad, cy, "Quick actions")
        cy += 26
        bw2 = (inner - 8) / 2
        for k, label in enumerate(["Offset Path", "Simplify", "Bring to Front", "Lock"]):
            button(t, dock, pad + (k % 2) * (bw2 + 8), cy + (k // 2) * (t["ctrl_h"] + 8), bw2, label)
    elif tab == "layers":
        sf = fr(dock, pad, cy, inner, t["ctrl_h"], "Search layers", t["field"], t["r_ctrl"], t["field_fx"],
                layout="horizontal", padding=[0, 8, 0, 8], gap=6, crossAlign="center")
        ic(sf, "search", 0, 0, 14, t["text3"])
        tx(sf, "Search layers", 0, 0, 12, t["text3"])
        cy += t["ctrl_h"] + 10
        rows = [("Layer 1", 0, True, None, False), ("Poster draft", 1, False, "T", False), ("Rectangle", 1, False, ART["rect"], False),
                ("Ellipse", 1, False, ART["circle"], True), ("Background", 0, False, None, False)]
        for name, depth, expanded, thumb, sel in rows:
            rh = t["row_h"]
            row = fr(dock, 0 if t["lines"] else 8, cy, dw if t["lines"] else dw - 16, rh, f"layer/{name}",
                     t["accent_soft"] if sel else None, 0 if t["lines"] else t["r_ctrl"])
            x = 10
            ic(row, "eye", x, (rh - 16) / 2, 16, t["text2"])
            x += 26 + depth * 18
            if depth == 0:
                ic(row, "chevron-down" if expanded else "chevron-right", x, (rh - 14) / 2, 14, t["text2"])
                x += 20
                tx(row, name, x, (rh - line_h(12)) / 2, 12, t["text1"], "SemiBold")
            else:
                th_ = fr(row, x, (rh - 20) / 2, 20, 20, "thumbnail", "#FFFFFF", t["r_swatch"], stroke=t["divider"])
                if thumb == "T":
                    tx(th_, "T", 6, 2, 12, ART["text"], "SemiBold")
                elif thumb == ART["circle"]:
                    el(th_, 4, 4, 12, 12, thumb)
                else:
                    rc(th_, 3, 5, 14, 10, thumb, 0)
                x += 28
                tx(row, name, x, (rh - line_h(12)) / 2, 12, t["text1"])
            rw = dw if t["lines"] else dw - 16
            if sel:
                rc(row, rw - 22, (rh - 8) / 2, 8, 8, t["accent"], t["r_swatch"] / 3, name="selected")
            ic(row, "circle", rw - 44, (rh - 12) / 2, 12, t["text3"] if not sel else t["accent"])
            cy += rh + (0 if t["lines"] else 2)
        foot_y = H - ah - sh - 40
        if t["lines"]:
            divider(t, dock, 0, foot_y, dw, 1)
        tx(dock, "2 layers", pad, foot_y + (40 - line_h(11)) / 2, 11, t["text3"])
        for k, name in enumerate(["file-plus", "dc-folder", "trash-2"]):
            icon_button(t, dock, dw - pad - 28 - k * 30, foot_y + 6, 28, name, 16)

    # Status bar: one row; the hint in the middle; numbers quiet.
    sb = fr(root, 0, H - sh, W, sh, "Status bar", t["appbar"])
    if t["lines"]:
        divider(t, sb, 0, 0, W, 1)
    y0 = (sh - t["ctrl_h"] + 6) / 2
    for x, w, s in [(8, 72, "95%"), (86, 56, "0°"), (148, 120, "Artboard 1")]:
        z = fr(sb, x, y0, w, t["ctrl_h"] - 6, f"status/{s}", None, t["r_ctrl"], layout="horizontal", padding=[0, 4, 0, 8],
               mainAlign="spaceBetween", crossAlign="center")
        tx(z, s, 0, 0, 11, t["text2"])
        ic(z, "chevron-down", 0, 0, 12, t["text3"])
    tx(sb, "Click to select   ·   ⇧ Click to add   ·   ⌥ Drag to duplicate", 300, (sh - line_h(11)) / 2, 11, t["text3"], name="hint")
    tx(sb, "render 3.7 ms     ui 1.4 ms     60 fps", W - 236, (sh - line_h(11)) / 2, 11, t["text3"], w=220, align="right", name="readouts")
    return root, hot


# ---------------------------------------------------------------- design-system sheet
def tokens_sheet(t, px, py, collection, mode):
    root = fr(None, px, py, W, H, f"{t['key']} · {t['name']} · Design system", t["chrome"])
    f.run("variable.setMode", ids=[root], collection=collection, mode=mode)
    tx(root, f"Proposal {t['key']} — {t['name']}: design system", 48, 40, 28, t["text1"], "SemiBold")
    tx(root, "Tokens are FigCraft variables (Local variables › " + collection + "). Swatches below are bound to them.", 48, 82, 13, t["text2"])
    # Colours
    tx(root, "Colour", 48, 130, 14, t["text1"], "SemiBold")
    roles = [("chrome", "Chrome: app bar, toolbar, rail, dock (one surface)"), ("pasteboard", "Canvas pasteboard"),
             ("divider", "Divider" + ("" if t["lines"] else " (canvas edge only)")), ("field", "Field"), ("raised", "Raised control"),
             ("text1", "Text"), ("text2", "Secondary text"), ("text3", "Tertiary text / hints"), ("icon", "Icon"),
             ("accent", "Accent: selection, focus, primary action — nothing else")]
    for k, (role, label) in enumerate(roles):
        x = 48 + (k % 5) * 268
        y = 160 + (k // 5) * 96
        sw = rc(root, x, y, 40, 40, t[role], t["r_ctrl"], stroke=t["divider"], name=f"token/{role}")
        if role in VARS.get(collection, {}):
            f.run("variable.bind", ids=[sw], field="fill", variable=VARS[collection][role])
        tx(root, role, x + 52, y + 2, 12, t["text1"], "SemiBold")
        tx(root, t[role].upper(), x + 52, y + 20, 11, t["text3"])
        tx(root, label, x, y + 48, 11, t["text2"], w=250)
    # Corners
    tx(root, "Corners — one scale", 48, 370, 14, t["text1"], "SemiBold")
    scale = [("0", 0, "Docked chrome: toolbar, rail, dock, bars"), (str(t["r_ctrl"]), t["r_ctrl"], "Controls: buttons, fields, tools, rows"),
             (str(t["r_float"]), t["r_float"], "Floating: task bar, menus, popovers, dialogs")]
    if t["r_tab"] == 999:
        scale.insert(2, ("full", 999, "Pills: panel tabs, toggles"))
    for k, (lbl, r, use) in enumerate(scale):
        x = 48 + k * 220
        rc(root, x, 404, 96, 64, t["raised"], r, t["raised_fx"], stroke=None if t["raised_fx"] else t["divider"], name=f"radius/{lbl}")
        tx(root, f"{lbl} px" if lbl != "full" else "full", x, 478, 12, t["text1"], "SemiBold")
        tx(root, use, x, 496, 11, t["text2"], w=200)
    # Type
    tx(root, "Type — Inter", 980, 370, 14, t["text1"], "SemiBold")
    for k, (s, st, use) in enumerate([(13, "SemiBold", "Window title"), (12, "SemiBold", "Section title, active tab"),
                                      (12, "Regular", "Body, values, labels"), (11, "Regular", "Hints, units, status")]):
        tx(root, f"{s} {st} — {use}", 980, 404 + k * 26, s, t["text1"] if k < 3 else t["text3"], st)
    # Controls
    tx(root, "Controls", 48, 560, 14, t["text1"], "SemiBold")
    button(t, root, 48, 594, 112, "Button")
    button(t, root, 172, 594, 112, "Primary", primary=True)
    field(t, root, 296, 594, 132, "W", "260", " pt")
    icon_button(t, root, 444, 594, t["tool_btn"], "pen-tool", t["tool_icon"])
    icon_button(t, root, 444 + t["tool_btn"] + 8, 594, t["tool_btn"], "dc-selection", t["tool_icon"], active=True)
    tx(root, "Tool: idle / active (neutral, not accent)", 444, 594 + t["tool_btn"] + 8, 11, t["text2"])
    task = fr(root, 760, 590, 10, 40, "Floating surface", t["float_fill"], t["r_float"], t["float_fx"], stroke=t["float_stroke"],
              layout="horizontal", padding=[0, 6, 0, 6], gap=2, crossAlign="center", sizingH="hug")
    for icon, label in [("pen-tool", "Edit Path"), ("copy", "Duplicate")]:
        b = fr(task, 0, 0, 10, 28, f"task/{label}", None, t["r_ctrl"], layout="horizontal", padding=[0, 8, 0, 8], gap=6, crossAlign="center", sizingH="hug")
        ic(b, icon, 0, 0, 16, t["icon"])
        tx(b, label, 0, 0, 12, t["text1"])
    tx(root, "Floating: the only surfaces with a shadow", 760, 640, 11, t["text2"])
    # Rules
    tx(root, "Rules", 48, 700, 14, t["text1"], "SemiBold")
    rules = [
        "No container inside a container: docked panels reach the window's edges; nothing docked is a card.",
        "Separation by tone" + (" and 1 px hairlines" if t["lines"] else " and space, not lines or boxes") + ".",
        "One corner scale (above). Nothing else is rounded; no hand-picked radii.",
        "Colour belongs to the artwork. The interface is neutral; the accent marks selection, focus and the primary action only.",
    ]
    for k, r in enumerate(rules):
        tx(root, f"{k + 1}.  {r}", 48, 732 + k * 26, 13, t["text1"])
    return root


VARS = {}


def make_variables():
    def coll(name, modes):
        r = f.run("variable.createCollection", name=name, modes=modes)
        return r["id"] if isinstance(r, dict) else r

    roles = ["chrome", "pasteboard", "divider", "field", "raised", "text1", "text2", "text3", "icon", "accent"]
    a = coll("VectorCraft · Flat", ["Dark", "Light"])
    VARS["VectorCraft · Flat"] = {r: f.run("variable.create", collection=a, name=f"color/{r}", type="color",
                                           values={"Dark": FLAT[r], "Light": FLAT_LIGHT[r]})["id"] for r in roles}
    b = coll("VectorCraft · Quiet", ["Light", "Dark"])
    VARS["VectorCraft · Quiet"] = {r: f.run("variable.create", collection=b, name=f"color/{r}", type="color",
                                            values={"Light": QUIET_LIGHT[r], "Dark": QUIET_DARK[r]})["id"] for r in roles}
    for coll_name, theme in [("VectorCraft · Flat", FLAT), ("VectorCraft · Quiet", QUIET_LIGHT)]:
        cid = a if theme is FLAT else b
        for k in ["r_ctrl", "r_float"]:
            f.run("variable.create", collection=cid, name=f"radius/{'control' if k == 'r_ctrl' else 'floating'}", type="number",
                  values={m: theme[k] for m in ["Light", "Dark"]})


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "probe"
    if step == "probe":
        th = {"A": FLAT, "B": QUIET_LIGHT, "BD": QUIET_DARK}[sys.argv[2]]
        tab = sys.argv[3]
        f.run("file.new", name="probe")
        fr_, hot = screen(th, tab, 0, 0)
        print(fr_, hot)
        print(f.call("ui.render", {"ids": [fr_], "path": f"{OUT}/probe-{sys.argv[2]}-{tab}.png", "scale": 1}))


# ---------------------------------------------------------------- full document
DOC_BG = "#F3F4F6"


def readme(px, py):
    t = QUIET_LIGHT
    root = fr(None, px, py, W, H, "Read me", "#FFFFFF")
    tx(root, "VectorCraft — a quieter interface", 72, 64, 36, t["text1"], "SemiBold")
    tx(root, "Two proposals for the interface since 0.12. Same layout, tools and panels; only the visual system changes.", 72, 116, 15, t["text2"])
    tx(root, "Prototype: Present (▶) on page A or B. Click the panel tabs (Properties / Layers); the sun in the app bar switches Dark and Light.", 72, 142, 13, t["text3"])
    y = 200
    tx(root, "What's wrong today", 72, y, 16, t["text1"], "SemiBold")
    issues = [
        ("Container in a container.", "The toolbar, the panel rail and the dock are rounded cards inside square columns, with a strip of window colour around each (theme::card, CARD_RADIUS = 8)."),
        ("No corner system.", "Ten different corner radii are hard-coded across 43 files of ui-egui (0, 1, 2, 3, 4, 5, 6, 8, 10 and 11 px). The theme's own radius token (4 px) is used in one place."),
        ("Colour competes with the artwork.", "The coral accent fills the active tool, buttons and the Discord button. In a design tool the art should be the most colourful thing on screen."),
    ]
    for k, (a, b) in enumerate(issues):
        tx(root, f"{k + 1}", 72, y + 36 + k * 64, 13, "#E5484D", "SemiBold")
        tx(root, a, 96, y + 36 + k * 64, 13, t["text1"], "SemiBold")
        tx(root, b, 96, y + 56 + k * 64, 13, t["text2"], w=560)
    y = 470
    tx(root, "Rules both proposals follow", 72, y, 16, t["text1"], "SemiBold")
    rules = ["Nothing docked is a card: panels reach the window's edges.",
             "One corner scale, from tokens. No hand-picked radii.",
             "The interface is neutral. The accent marks selection, focus and the primary action only.",
             "Shadows only on what floats (task bar, menus, dialogs)."]
    for k, r in enumerate(rules):
        tx(root, f"·  {r}", 72, y + 34 + k * 24, 13, t["text1"])
    x2 = 760
    tx(root, "A · Flat", x2, 200, 16, t["text1"], "SemiBold")
    tx(root, "Today's look without the cards, in Dark and Light. Docked panels flush to the edges and divided by 1 px hairlines. Corners 0 / 4 / 8. Underlined panel tabs. The active tool is a neutral grey, not coral.",
       x2, 228, 13, t["text2"], w=600)
    tx(root, "B · Quiet", x2, 330, 16, t["text1"], "SemiBold")
    tx(root, "Calmer, after soft monochrome interfaces. All chrome is one continuous surface; tone and space separate things instead of lines. Raised controls and floating surfaces get soft depth; fields sit slightly inset. Corners 0 / 8 / pill / 14. Segmented panel tabs. Light and Dark.",
       x2, 358, 13, t["text2"], w=600)
    tx(root, "B takes the references' softness, not their nested cards: nothing docked sits inside a box.", x2, 450, 13, t["text1"], w=600)
    tx(root, "Pages", x2, 520, 16, t["text1"], "SemiBold")
    for k, p in enumerate(["Current (0.13) — today's window and the three problems",
                           "A · Flat — design system, Dark and Light, Properties and Layers",
                           "B · Quiet — design system, Light and Dark, Properties and Layers",
                           "Overview — every look side by side"]):
        tx(root, p, x2, 552 + k * 24, 13, t["text2"])
    tx(root, "Icons: VectorCraft's own (assets/icons). Font: Inter. Nothing from other apps.", 72, H - 48, 11, t["text3"])
    return root


def current_page():
    root = fr(None, 0, 0, W, H, "Current 0.13 · Properties", "#000000")
    img = f.run("image.place", path=f"{OUT}/current.png", x=0, y=0, width=W, height=H, parent=root)["id"]
    f.run("node.set", ids=[img], props={"name": "screenshot (VectorCraft 0.13.1, Modern, Medium Dark)"})
    x = W + 60
    marks = [(44, 431, 1), (1138, 431, 1), (1377, 275, 1), (1424, 606, 2), (1345, 418, 2), (50, 72, 3), (1266, 15, 3)]
    for mx, my, n in marks:
        m = fr(root, mx - 13, my - 13, 26, 26, f"marker {n}", "#E5484D", 999, layout="horizontal", mainAlign="center", crossAlign="center")
        tx(m, str(n), 0, 0, 13, "#FFFFFF", "SemiBold")
    notes = [
        ("1  Container in a container", "Toolbar, rail and dock are rounded cards inside square columns, with a strip of window colour around each."),
        ("2  No corner system", "Ten hard-coded radii (0–11 px) across 43 files; the 4 px token is used once. Fields, buttons, tabs, swatches and panels each round differently."),
        ("3  Colour competes with the art", "Coral fills the active tool and primary buttons; the Discord button is tinted. The artwork should be the most colourful thing on screen."),
    ]
    nx = x + 40
    for k, (a, b) in enumerate(notes):
        tx(None, a, nx, k * 120, 16, "#E5484D", "SemiBold")
        tx(None, b, nx, k * 120 + 28, 13, "#1F2328", w=360)
    return root


def build_all():
    f.run("file.new", name="VectorCraft UI proposal")
    make_variables()
    pages = f.run("page.list")
    first = (pages.get("pages") if isinstance(pages, dict) else pages)[0]
    f.run("page.rename", id=first["id"], name="Read me")
    f.run("page.setBackground", color=DOC_BG)
    readme(0, 0)

    f.run("page.add", name="Current (0.13)")
    f.run("page.setBackground", color=DOC_BG)
    cur = current_page()

    f.run("page.add", name="A · Flat")
    f.run("page.setBackground", color=DOC_BG)
    tokens_sheet(FLAT, 0, 0, "VectorCraft · Flat", "Dark")
    tokens_sheet(FLAT_LIGHT, 0, 1000, "VectorCraft · Flat", "Light")
    a_props, ha = screen(FLAT, "properties", 1540, 0)
    a_layers, hb = screen(FLAT, "layers", 3080, 0)
    al_props, hc = screen(FLAT_LIGHT, "properties", 1540, 1000)
    al_layers, hd = screen(FLAT_LIGHT, "layers", 3080, 1000)
    for h, props, layers, other in [(ha, a_props, a_layers, al_props), (hb, a_props, a_layers, al_layers),
                                    (hc, al_props, al_layers, a_props), (hd, al_props, al_layers, a_layers)]:
        interact(h["properties"], props)
        interact(h["layers"], layers)
        interact(h["theme"], other)
    f.run("proto.flow.add", start=a_props, name="Flat")

    f.run("page.add", name="B · Quiet")
    f.run("page.setBackground", color=DOC_BG)
    tokens_sheet(QUIET_LIGHT, 0, 0, "VectorCraft · Quiet", "Light")
    tokens_sheet(QUIET_DARK, 0, 1000, "VectorCraft · Quiet", "Dark")
    lp, h1 = screen(QUIET_LIGHT, "properties", 1540, 0)
    ll, h2 = screen(QUIET_LIGHT, "layers", 3080, 0)
    dp, h3 = screen(QUIET_DARK, "properties", 1540, 1000)
    dl, h4 = screen(QUIET_DARK, "layers", 3080, 1000)
    for h, props, layers, other in [(h1, lp, ll, dp), (h2, lp, ll, dl), (h3, dp, dl, lp), (h4, dp, dl, ll)]:
        interact(h["properties"], props)
        interact(h["layers"], layers)
        interact(h["theme"], other)
    f.run("proto.flow.add", start=lp, name="Quiet")

    frames = {"current": cur, "a-dark-properties": a_props, "a-dark-layers": a_layers, "a-light-properties": al_props,
              "a-light-layers": al_layers, "b-light-properties": lp,
              "b-light-layers": ll, "b-dark-properties": dp, "b-dark-layers": dl}
    return frames


def export(frames):
    os.makedirs(f"{OUT}/png", exist_ok=True)
    for name, i in frames.items():
        f.call("ui.render", {"ids": [i], "path": f"{OUT}/png/{name}.png", "scale": 2})


def overview(frames):
    f.run("page.add", name="Overview")
    f.run("page.setBackground", color=DOC_BG)
    root = fr(None, 0, 0, 2290, 1060, "Overview", "#FFFFFF")
    tiles = [(0, 0, "current", "Current (0.13)"), (1, 0, "a-dark-properties", "A · Flat — Dark"), (2, 0, "a-light-properties", "A · Flat — Light"),
             (1, 1, "b-dark-properties", "B · Quiet — Dark"), (2, 1, "b-light-properties", "B · Quiet — Light")]
    for col, row, key, label in tiles:
        x, y = 40 + col * 750, 40 + row * 510
        tx(root, label, x, y, 16, "#1F2328", "SemiBold")
        i = f.run("image.place", path=f"{OUT}/png/{key}.png", x=x, y=y + 30, width=720, height=450, parent=root)["id"]
        f.run("node.set", ids=[i], props={"name": label, "cornerRadius": 8, "effects": [SHADOW("#0000001F", 2, 10)]})
    tx(root, "Both proposals come in Dark and Light.", 40, 580, 16, "#1F2328", "SemiBold")
    tx(root, "A · Flat: today's look without the cards; 1 px hairlines; corners 0 / 4 / 8.\n\nB · Quiet: one continuous surface, no lines; soft depth on raised controls; corners 0 / 8 / pill / 14.\n\nIn both, the accent (blue) marks selection, focus and the primary action only.",
       40, 616, 13, "#646A73", w=640)


if __name__ == "__main__" and sys.argv[1:2] == ["all"]:
    frames = build_all()
    export(frames)
    overview(frames)
    for name in ["Read me", "A · Flat", "B · Quiet"]:
        pass
    path = f"{OUT}/VectorCraft UI proposal.figcraft"
    print(f.run("file.saveAs", path=path))
    print(json.dumps(frames))
