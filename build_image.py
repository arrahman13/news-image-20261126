#!/usr/bin/env python3
"""Render the 26 November 2026 newspaper image (entry.png).

Build-time only: the grading sandbox never runs this file. It reads
stories.py, the three AI lead photos in leads/, and the Natural Earth
110m land polygons in map_data/, and composes one 1024x1024 page.

Layout (1024x1024): masthead + date check, UTC timeline, three
photorealistic leads, a world map drawn from real coastline data with
16 numbered pins, and a 5x8 grid of 40 verified stories.
"""

import hashlib
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from stories import DATE_LINE, LEADS, LEGEND, PIN_OFFSETS, PINS, REGIONS, STORIES, TIMELINE

HERE = Path(__file__).resolve().parent
W, H = 1024, 1024
MARGIN = 14
CW = W - 2 * MARGIN  # 996

PAPER = (248, 244, 236)
INK = (25, 25, 25)
RED = (176, 39, 24)
GRAY = (109, 100, 85)
RULE = (120, 110, 92)
OCEAN = (216, 232, 240)
LAND = (231, 223, 201)
LAND_LINE = (179, 168, 143)
MAP_BORDER = (138, 127, 102)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def truncate(draw, text, fnt, width):
    """Shorten with an ellipsis so the text fits on one line."""
    if draw.textlength(text, font=fnt) <= width:
        return text
    while text and draw.textlength(text + "...", font=fnt) > width:
        text = text[:-1].strip()
    return text + "..."


def draw_map(draw, x, y, w, h):
    """World map from the Natural Earth 110m land polygons."""
    draw.rectangle([x, y, x + w, y + h], fill=OCEAN, outline=MAP_BORDER, width=1)
    data = json.loads((HERE / "map_data" / "ne_110m_land.geojson").read_text())
    lon0, lon1 = -180.0, 180.0
    lat0, lat1 = 90.0, -90.0

    def project(lon, lat):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        return (px, py)

    def draw_ring(ring):
        pts, cur = [], []
        prev_lon = None
        for lon, lat in ring:
            if prev_lon is not None and abs(lon - prev_lon) > 180.0:
                if len(cur) > 2:
                    pts.append(cur)
                cur = []
            cur.append(project(lon, lat))
            prev_lon = lon
        if len(cur) > 2:
            pts.append(cur)
        for poly in pts:
            draw.polygon(poly, fill=LAND, outline=LAND_LINE)

    for feature in data["features"]:
        geom = feature["geometry"]
        if geom["type"] == "Polygon":
            for ring in geom["coordinates"]:
                draw_ring(ring)
        elif geom["type"] == "MultiPolygon":
            for polygon in geom["coordinates"]:
                for ring in polygon:
                    draw_ring(ring)
    # graticule: equator + tropics, faint
    for lat in (0.0, 23.44, -23.44):
        gy = y + (lat0 - lat) / (lat0 - lat1) * h
        draw.line([(x, gy), (x + w, gy)], fill=(190, 205, 212), width=1)


def draw_pins(draw, x, y, w, h):
    lon0, lon1 = -180.0, 180.0
    lat0, lat1 = 90.0, -90.0
    fnt = font(SANS_BOLD, 10)
    for number, _label, lon, lat in PINS:
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        dx, dy = PIN_OFFSETS.get(number, (0, 0))
        cx, cy = px + dx, py + dy
        if (dx, dy) != (0, 0):
            draw.line([(px, py), (cx, cy)], fill=RED, width=1)
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        r = 9
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=(255, 255, 255), width=2)
        text = str(number)
        tw = draw.textlength(text, font=fnt)
        draw.text((cx - tw / 2, cy - 7), text, font=fnt, fill=(255, 255, 255))


def center_crop(im, tw, th):
    """Center-crop an image to the target aspect, then resize."""
    sw, sh = im.size
    target = tw / th
    src = sw / sh
    if src > target:
        nw = int(sh * target)
        left = (sw - nw) // 2
        im = im.crop((left, 0, left + nw, sh))
    else:
        nh = int(sw / target)
        top = (sh - nh) // 2
        im = im.crop((0, top, sw, top + nh))
    return im.resize((tw, th), Image.LANCZOS)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------
    f_mast = font(SERIF, 44)
    title = "THE WORLD IN ONE IMAGE"
    tw = draw.textlength(title, font=f_mast)
    draw.text(((W - tw) / 2, 4), title, font=f_mast, fill=INK)
    f_sub = font(SANS_BOLD, 13)
    f_sub2 = font(SANS, 12)
    draw.text((MARGIN, 56), DATE_LINE, font=f_sub, fill=INK)
    mid = "40 VERIFIED STORIES  •  9 REGIONS"
    tw = draw.textlength(mid, font=f_sub2)
    draw.text(((W - tw) / 2, 57), mid, font=f_sub2, fill=GRAY)
    check = "DATE CHECK ✓ 26 NOV 2026"
    tw = draw.textlength(check, font=f_sub)
    draw.text((W - MARGIN - tw, 56), check, font=f_sub, fill=RED)
    draw.line([(MARGIN, 74), (W - MARGIN, 74)], fill=RULE, width=2)

    # ---- UTC timeline ---------------------------------------------
    f_tl_b = font(SANS_BOLD, 10)
    f_tl = font(SANS, 10)
    label = "UTC TIMELINE  "
    draw.text((MARGIN, 80), label, font=f_tl_b, fill=RED)
    x = MARGIN + draw.textlength(label, font=f_tl_b)
    parts = []
    for time, event in TIMELINE:
        parts.append("%s %s" % (time, event))
    line = "   •   ".join(parts)
    avail = (W - MARGIN) - x
    draw.text((x, 80), truncate(draw, line, f_tl, avail), font=f_tl, fill=INK)
    draw.line([(MARGIN, 98), (W - MARGIN, 98)], fill=RULE, width=1)

    # ---- Three photorealistic leads -------------------------------
    lead_w, lead_h = 322, 128
    gap = (CW - 3 * lead_w) // 2
    f_cap_h = font(SANS_BOLD, 12)
    f_cap_s = font(SANS, 10)
    f_cap_p = font(SANS_BOLD, 8)
    for i, (rel, headline, summary, photo_tag) in enumerate(LEADS):
        lx = MARGIN + i * (lead_w + gap)
        photo = Image.open(HERE / rel).convert("RGB")
        photo = center_crop(photo, lead_w, lead_h)
        img.paste(photo, (lx, 104))
        draw.rectangle([lx, 104, lx + lead_w, 104 + lead_h], outline=INK, width=1)
        draw.text((lx, 236), truncate(draw, headline, f_cap_h, lead_w), font=f_cap_h, fill=INK)
        draw.text((lx, 252), truncate(draw, summary, f_cap_s, lead_w), font=f_cap_s, fill=GRAY)
        draw.text((lx, 266), photo_tag, font=f_cap_p, fill=RED)
    draw.line([(MARGIN, 282), (W - MARGIN, 282)], fill=RULE, width=1)

    # ---- World map -------------------------------------------------
    f_map_t = font(SANS_BOLD, 11)
    draw.text((MARGIN, 288), "WORLD MAP — 16 NUMBERED PINS  •  COASTLINE: NATURAL EARTH",
              font=f_map_t, fill=INK)
    map_x, map_y, map_w, map_h = MARGIN, 306, CW, 164
    draw_map(draw, map_x, map_y, map_w, map_h)
    draw_pins(draw, map_x, map_y, map_w, map_h)
    f_leg = font(SANS, 9)
    draw.text((MARGIN, 474), LEGEND, font=f_leg, fill=GRAY)
    draw.line([(MARGIN, 490), (W - MARGIN, 490)], fill=RULE, width=1)

    # ---- Story grid: 5 columns x 8 rows ---------------------------
    cols, rows = 5, 8
    col_gap = 10
    col_w = (CW - (cols - 1) * col_gap) // cols
    grid_y = 496
    grid_h = 1010 - grid_y
    cell_h = grid_h // rows
    f_tag = font(SANS_BOLD, 8)
    f_head = font(SANS_BOLD, 11)
    f_body = font(SANS, 9)
    for idx, (number, region, _city, headline, summary) in enumerate(STORIES):
        col = idx % cols
        row = idx // cols
        cx = MARGIN + col * (col_w + col_gap)
        cy = grid_y + row * cell_h
        tag = "%02d · %s" % (number, region)
        draw.text((cx, cy + 1), tag, font=f_tag, fill=RED)
        head_lines = wrap(draw, headline, f_head, col_w)[:2]
        by = cy + 13
        for line in head_lines:
            draw.text((cx, by), line, font=f_head, fill=INK)
            by += 13
        body_lines = wrap(draw, summary, f_body, col_w)[:2]
        by = cy + 13 + 2 * 13
        for line in body_lines:
            draw.text((cx, by), line, font=f_body, fill=(60, 60, 60))
            by += 11

    # ---- Footer ----------------------------------------------------
    f_foot = font(SANS, 9)
    foot = ("40 stories verified 26 Nov 2026  •  Sources: BBC, Reuters, AP, AFP, "
            "The Guardian, France 24  •  make.fun/bounty/news-image-20261126")
    tw = draw.textlength(foot, font=f_foot)
    draw.text(((W - tw) / 2, 1012), foot, font=f_foot, fill=GRAY)

    out = HERE / "entry.png"
    img.save(out, optimize=True)
    data = out.read_bytes()
    print("entry.png: %d bytes, %dx%d, sha256 %s" % (len(data), W, H, hashlib.sha256(data).hexdigest()))
    print("stories: %d, regions: %d, pins: %d" % (len(STORIES), len(REGIONS), len(PINS)))
    assert len(data) <= 1024 * 1024, "entry.png over 1 MiB"


if __name__ == "__main__":
    main()
