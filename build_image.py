#!/usr/bin/env python3
"""Build entry.png for news-image-20261126 v2.

One-page newspaper: navy top bar, giant date, red headline strip,
coloured region chips, fields bar, big-stat bar, 3 photo leads,
10 illustrated stories, Natural Earth map + numbered list, date check.
Run: python3 build_image.py  -> writes entry.png next to this file.
"""

import json
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

from stories import FIELDS, LEADS, LISTED, PINS, REGIONS, SMALL, STATS, UTC_TIMELINE

HERE = os.path.dirname(os.path.abspath(__file__))
LEADS_DIR = os.path.join(HERE, "leads")
GEOJSON = os.path.join(HERE, "map_data", "ne_110m_land.geojson")

W, H = 1024, 1024
BG = (247, 243, 234)          # warm paper
INK = (26, 26, 26)
NAVY = (16, 36, 62)
RED = (185, 28, 28)
GOLD = (245, 197, 66)
PAPER_LINE = (210, 198, 175)

FD = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(text, fnt, max_w):
    """Greedy wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def crop_to(img, tw, th):
    """Centre-crop to the target aspect, then resize."""
    sw, sh = img.size
    ta, sa = tw / th, sw / sh
    if sa > ta:
        nw = int(sh * ta)
        x0 = (sw - nw) // 2
        img = img.crop((x0, 0, x0 + nw, sh))
    else:
        nh = int(sw / ta)
        y0 = (sh - nh) // 2
        img = img.crop((0, y0, sw, y0 + nh))
    return img.resize((tw, th), Image.LANCZOS)


def draw_badge(d, x, y, text, fnt):
    """Small outlined badge (OFFICIAL / REPORTED / CLAIM)."""
    w = int(fnt.getlength(text)) + 8
    h = 12
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1, fill=(255, 255, 255))
    d.text((x + 4, y + 1), text, font=fnt, fill=INK)
    return w


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    X0, X1 = 8, 1016
    PW = X1 - X0  # 1008
    y = 0

    # ---- top bar (navy) ----
    d.rectangle([0, y, W, y + 22], fill=NAVY)
    d.text((X0, y + 4), "THE WORLD IN ONE DAY", font=SANS_B(12), fill=GOLD)
    right = "50 STORIES \u2022 10 REGIONS \u2022 22 FIELDS \u2022 ALL FIRST REPORTED ON THURSDAY 26 NOVEMBER 2026"
    d.text((X1 - SANS_B(9).getlength(right), y + 6), right, font=SANS_B(9), fill=(255, 255, 255))
    y += 22

    # ---- giant date ----
    d.text((W // 2, y + 2), "Thursday 26 November 2026", font=SERIF_B(50),
           fill=INK, anchor="ma")
    y += 52
    d.line([X0, y, X1, y], fill=PAPER_LINE, width=1)
    y += 2

    # ---- red headline strip ----
    strip = "US proposes tariffs on 14 economies \u00b7 Cairo tanker fire kills 31 \u00b7 Pakistan\u2019s first astronaut docks at Tiangong"
    d.text((W // 2, y + 2), strip, font=SERIF_B(15), fill=RED, anchor="ma")
    y += 20
    d.line([X0, y, X1, y], fill=PAPER_LINE, width=1)
    y += 3

    # ---- region chips ----
    chip_y = y
    total_text = sum(SANS_B(8).getlength(f"{n} {c}") for n, c, _ in REGIONS)
    gaps = 2 * (len(REGIONS) - 1)
    widths = [int(PW * SANS_B(8).getlength(f"{n} {c}") / total_text) for n, c, _ in REGIONS]
    widths[0] += PW - gaps - sum(widths)
    cx = X0
    for (name, count, color), w in zip(REGIONS, widths):
        d.rectangle([cx, chip_y, cx + w, chip_y + 19], fill=color)
        d.text((cx + w // 2, chip_y + 5), f"{name} {count}", font=SANS_B(8),
               fill=(255, 255, 255), anchor="ma")
        cx += w + 2
    y = chip_y + 19 + 3

    # ---- fields bar ----
    fields_txt = " \u00b7 ".join(f"{n} {c}" for n, c in FIELDS)
    d.text((X0, y), "22 FIELDS", font=SANS_B(9), fill=INK)
    fx = X0 + SANS_B(9).getlength("22 FIELDS") + 8
    d.text((fx, y), fields_txt, font=SANS(9), fill=(60, 60, 60))
    y += 15
    d.line([X0, y, X1, y], fill=PAPER_LINE, width=1)
    y += 3

    # ---- big stat bar ----
    stat_h = 48
    cw = PW // 5
    for i, (num, label, color) in enumerate(STATS):
        cx0 = X0 + i * cw
        if i:
            d.line([cx0 - 3, y + 4, cx0 - 3, y + stat_h - 4], fill=PAPER_LINE, width=1)
        d.text((cx0 + cw // 2, y), num, font=SANS_B(26), fill=color, anchor="ma")
        for j, ln in enumerate(label.split("\n")):
            d.text((cx0 + cw // 2, y + 27 + j * 10), ln, font=SANS(9),
                   fill=(60, 60, 60), anchor="ma")
    y += stat_h
    d.line([X0, y, X1, y], fill=PAPER_LINE, width=1)
    y += 4

    # ---- 3 big leads ----
    lead_w = (PW - 2 * 9) // 3
    lead_img_h = 112
    lead_top = y
    for i, lead in enumerate(LEADS):
        lx = X0 + i * (lead_w + 9)
        color = dict((n, c) for n, c, _ in REGIONS)[lead["region"]]
        d.rectangle([lx, y, lx + lead_w, y + 3], fill=color)
        ly = y + 3
        photo = crop_to(Image.open(os.path.join(LEADS_DIR, lead["image"])).convert("RGB"),
                        lead_w, lead_img_h)
        img.paste(photo, (lx, ly))
        # number badge
        d.ellipse([lx + 4, ly + 4, lx + 26, ly + 26], fill=RED, outline=(255, 255, 255), width=2)
        d.text((lx + 15, ly + 8), str(lead["n"]), font=SANS_B(13), fill=(255, 255, 255), anchor="ma")
        ty = ly + lead_img_h + 4
        d.text((lx, ty), lead["tag"], font=SANS_B(9), fill=RED)
        bw = draw_badge(d, lx + lead_w - 62, ty - 1, lead["badge"], SANS_B(8))
        ty += 13
        for j, ln in enumerate(wrap(lead["headline"], SERIF_B(15), lead_w)[:3]):
            d.text((lx, ty + j * 17), ln, font=SERIF_B(15), fill=INK)
        ty += 17 * min(3, len(wrap(lead["headline"], SERIF_B(15), lead_w)))
        for j, ln in enumerate(wrap(lead["summary"], SANS(10), lead_w)[:2]):
            d.text((lx, ty + j * 12), ln, font=SANS(10), fill=(50, 50, 50))
        ty += 12 * min(2, len(wrap(lead["summary"], SANS(10), lead_w))) + 2
        why_lines = wrap("WHY IT MATTERS  " + lead["why"], SANS(9), lead_w)
        d.text((lx, ty), "WHY IT MATTERS", font=SANS_B(8), fill=RED)
        wx = lx + SANS_B(8).getlength("WHY IT MATTERS") + 4
        for j, ln in enumerate(why_lines):
            if j == 0:
                ln = ln[len("WHY IT MATTERS"):].strip()
            d.text((wx if j == 0 else lx, ty + j * 11), ln, font=SANS(9), fill=INK)
    y = lead_top + 3 + lead_img_h + 4 + 13 + 51 + 24 + 24 + 4
    d.line([X0, y, X1, y], fill=PAPER_LINE, width=1)
    y += 4

    # ---- 10 small illustrated stories, two rows of five ----
    small_w = (PW - 4 * 6) // 5
    small_img_h = 74
    for row in range(2):
        row_top = y
        for i in range(5):
            s = SMALL[row * 5 + i]
            sx = X0 + i * (small_w + 6)
            color = dict((n, c) for n, c, _ in REGIONS)[s["region"]]
            d.rectangle([sx, y, sx + small_w, y + 3], fill=color)
            sy = y + 3
            photo = crop_to(Image.open(os.path.join(LEADS_DIR, s["image"])).convert("RGB"),
                            small_w, small_img_h)
            img.paste(photo, (sx, sy))
            d.ellipse([sx + 3, sy + 3, sx + 21, sy + 21], fill=RED, outline=(255, 255, 255), width=2)
            d.text((sx + 12, sy + 6), str(s["n"]), font=SANS_B(11), fill=(255, 255, 255), anchor="ma")
            ty = sy + small_img_h + 3
            d.text((sx, ty), s["tag"], font=SANS_B(8), fill=RED)
            ty += 11
            hl = wrap(s["headline"], SANS_B(10), small_w)[:3]
            for j, ln in enumerate(hl):
                d.text((sx, ty + j * 12), ln, font=SANS_B(10), fill=INK)
            ty += 12 * len(hl) + 1
            for j, ln in enumerate(wrap(s["summary"], SANS(8), small_w)[:2]):
                d.text((sx, ty + j * 10), ln, font=SANS(8), fill=(60, 60, 60))
        y = row_top + 3 + small_img_h + 3 + 11 + 36 + 21 + 6
    d.line([X0, y, X1, y], fill=PAPER_LINE, width=1)
    y += 4

    # ---- WHERE IT HAPPENED ----
    d.text((X0, y), "WHERE IT HAPPENED", font=SANS_B(11), fill=INK)
    d.text((X1, y + 2), "dots = story numbers", font=SANS(8), fill=(90, 90, 90), anchor="ra")
    y += 15
    map_x, map_w = X0, 360
    map_h = 200
    list_x, list_w = X0 + 368, PW - 368
    # map background
    d.rectangle([map_x, y, map_x + map_w, y + map_h], fill=(214, 232, 245))
    with open(GEOJSON) as f:
        gj = json.load(f)
    lon0, lon1, lat0, lat1 = -180, 180, -58, 84

    def proj(lon, lat):
        px = map_x + (lon - lon0) / (lon1 - lon0) * map_w
        py = y + (lat1 - lat) / (lat1 - lat0) * map_h
        return px, py

    def draw_poly(coords, depth=0):
        if depth == 0 and isinstance(coords[0][0], (list, tuple)):
            for ring in coords:
                draw_poly(ring, 1)
            return
        pts = [proj(lon, lat) for lon, lat in coords]
        if len(pts) > 1:
            d.polygon(pts, fill=(232, 220, 200), outline=(150, 135, 110))

    for feat in gj["features"]:
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            draw_poly(geom["coordinates"])
        elif geom["type"] == "MultiPolygon":
            for poly in geom["coordinates"]:
                draw_poly(poly)
    # pins
    for n, label, lon, lat, dx, dy in PINS:
        px, py = proj(lon, lat)
        qx, qy = px + dx, py + dy
        if dx or dy:
            d.line([px, py, qx, qy], fill=RED, width=1)
        d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=RED, outline=(255, 255, 255), width=1)
        d.text((qx, qy - 5), str(n), font=SANS_B(8), fill=(255, 255, 255), anchor="ma")
    # region legend under map (two rows of five)
    legend = ["N. America", "Latin Am.", "Europe", "Middle East", "N. Africa",
              "Sub-Saharan", "S. Asia", "E & SE Asia", "Oceania", "Global"]
    ly = y + map_h + 3
    for ri in range(2):
        lx = map_x
        for k in range(5):
            name, count, color = REGIONS[ri * 5 + k]
            d.ellipse([lx, ly + 1, lx + 7, ly + 8], fill=color)
            d.text((lx + 10, ly), legend[ri * 5 + k], font=SANS(7), fill=(60, 60, 60))
            lx += 10 + SANS(7).getlength(legend[ri * 5 + k]) + 8
        ly += 10
    # numbered list, three columns, title only (like the reference)
    cols = [LISTED[i::3] for i in range(3)]
    col_w = list_w // 3 - 4
    list_bottom = y
    for ci, col in enumerate(cols):
        cx = list_x + ci * (list_w // 3)
        cy = y
        for n, loc, headline, summary in col:
            head = f"{n} {loc} \u2014 {headline}"
            for ln in wrap(head, SANS_B(8), col_w)[:2]:
                d.text((cx, cy), ln, font=SANS_B(8), fill=INK)
                cy += 8
            cy += 1
        list_bottom = max(list_bottom, cy)
    y = max(y + map_h + 16, list_bottom)
    d.line([X0, y, X1, y], fill=PAPER_LINE, width=1)
    y += 4

    # ---- date check bar ----
    d.rectangle([X0, y, X0 + 78, y + 13], fill=RED)
    d.text((X0 + 39, y + 2), "DATE CHECK", font=SANS_B(9), fill=(255, 255, 255), anchor="ma")
    d.text((X0 + 84, y + 1), "Every story above happened or was first reported on Thursday 26 November 2026.",
           font=SANS_B(9), fill=INK)
    y += 15
    d.text((X0, y), "OFFICIAL", font=SANS_B(8), fill=RED)
    d.text((X0 + 46, y), "an authority's own figure or act", font=SANS(8), fill=(60, 60, 60))
    d.text((X0 + 230, y), "REPORTED", font=SANS_B(8), fill=RED)
    d.text((X0 + 286, y), "press report", font=SANS(8), fill=(60, 60, 60))
    d.text((X0 + 360, y), "CLAIM", font=SANS_B(8), fill=RED)
    d.text((X0 + 394, y), "one-sided account", font=SANS(8), fill=(60, 60, 60))
    d.text((X1, y), "Sources: BBC, Reuters, AP, AFP, The Guardian, France 24, Al Jazeera, CNBC, Yonhap, RNZ.",
           font=SANS(8), fill=(60, 60, 60), anchor="ra")
    y += 12
    d.text((X0, y), "UTC timeline: " + "  \u00b7  ".join(f"{t} {e}" for t, e in UTC_TIMELINE) +
           "   \u2014   Every drawing original.",
           font=SANS(8), fill=(90, 90, 90))

    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
