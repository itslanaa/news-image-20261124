#!/usr/bin/env python3
"""Draw the 24 November 2026 world-news front page (1024x1024 PNG).
Fresh renderer for news-image-20261124. DejaVu fonts only (no Liberation),
with a resilient font() so a missing font never crashes the run.
Deterministic: fixed seed, no network, no time dependence.
"""
import hashlib
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(OUT, exist_ok=True)

INK = (18, 18, 22)
PAPER = (250, 248, 242)
RED = (178, 34, 34)
BLUE = (28, 68, 128)
TEAL = (14, 110, 110)
GOLD = (176, 128, 20)
GREY = (90, 90, 96)
LIGHT = (232, 228, 220)

F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    for cand in (path, F_SANS, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(cand, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


def hline(draw, x0, x1, y, fill, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- layout
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
M = 34  # margin

# Masthead
d.rectangle([0, 0, W, 118], fill=INK)
draw_centered(d, W // 2, 16, "THE WORLD IN ONE DAY", font(F_SERIF_B, 44), PAPER)
draw_centered(d, W // 2, 70, "Tuesday 24 November 2026  ·  The day's news, in one picture",
              font(F_SANS, 19), (200, 196, 188))
hline(d, M, W - M, 128, INK, 3)

# ---- Lead stories: three big illustrated panels across the top ----
LEADS = [
    ("BENGHAZI", "Ukraine sinks Russian warship off Libya",
     "Zelensky: seven naval drones sank the corvette Merkury in port.",
     (178, 34, 34)),
    ("TECH", "Nvidia brings back Huang as chief executive",
     "Board reinstates Jensen Huang; shares jump 31% in a day.",
     (28, 68, 128)),
    ("HORMUZ", "Iran says three tankers hit mines",
     "Tankers burn in the Strait; Tehran refuses talks for now.",
     (14, 110, 110)),
]
lx, ly, lw, lh = M, 140, 308, 218
for i, (kicker, head, sub, col) in enumerate(LEADS):
    x = lx + i * (lw + 16)
    d.rectangle([x, ly, x + lw, ly + 92], fill=col)
    # simple scene: sun/sea for Benghazi, chip for Tech, waves for Hormuz
    if i == 0:
        d.ellipse([x + 200, ly + 14, x + 262, ly + 76], fill=(255, 214, 90))
        d.rectangle([x, ly + 62, x + lw, ly + 92], fill=(30, 60, 110))
        d.polygon([(x + 60, ly + 62), (x + 130, ly + 30), (x + 200, ly + 62)], fill=(120, 120, 130))
    elif i == 1:
        d.rectangle([x + 104, ly + 18, x + 204, ly + 74], fill=(20, 20, 26))
        for k in range(4):
            d.rectangle([x + 92, ly + 26 + k * 12, x + 104, ly + 34 + k * 12], fill=(200, 200, 210))
            d.rectangle([x + 204, ly + 26 + k * 12, x + 216, ly + 34 + k * 12], fill=(200, 200, 210))
        d.text((x + 128, ly + 34), "NVDA", font=font(F_SANS_B, 22), fill=(120, 220, 120))
    else:
        for k in range(3):
            yy = ly + 22 + k * 22
            d.arc([x + 30, yy, x + 278, yy + 34], 0, 180, fill=(255, 255, 255), width=5)
        d.rectangle([x + 40, ly + 40, x + 110, ly + 62], fill=(40, 40, 44))
        d.rectangle([x + 150, ly + 52, x + 240, ly + 72], fill=(60, 60, 66))
    d.text((x + 4, ly + 100), kicker, font=font(F_SANS_B, 15), fill=col)
    for j, ln in enumerate(wrap(d, head, font(F_SERIF_B, 21), lw)):
        d.text((x + 4, ly + 122 + j * 26), ln, font=font(F_SERIF_B, 21), fill=INK)
    for j, ln in enumerate(wrap(d, sub, font(F_SANS, 14), lw)):
        d.text((x + 4, ly + 178 + j * 18), ln, font=font(F_SANS, 14), fill=GREY)

# ---- Stats bar ----
hline(d, M, W - M, 372, INK, 2)
STATS = [("96", "DRONES AT UKRAINE"), ("700,000", "RUSSIAN DEAD"),
         ("31%", "NVIDIA JUMP"), ("26", "KILLED IN FACTORY FIRE"),
         ("7", "NAVAL DRONES"), ("3", "TANKERS HIT")]
sx = M
for num, lab in STATS:
    f1, f2 = font(F_SERIF_B, 26), font(F_SANS_B, 11)
    w1 = d.textlength(num, font=f1)
    d.text((sx, 382), num, font=f1, fill=RED)
    d.text((sx, 414), lab, font=f2, fill=GREY)
    sx += max(w1, d.textlength(lab, font=f2)) + 22
hline(d, M, W - M, 442, INK, 2)

# ---- Region columns ----
REGIONS = [
    ("EUROPE", BLUE, [
        "96-drone night hits Zaporizhzhia: 2 killed",
        "Russia warns Estonia: moves risk open war",
        "NATO sends AWACS to Poland after missiles",
        "Russian drone violates Polish airspace",
        "Germany first to use Ukraine Delta system",
        "EU proposes 22nd sanctions, sports ban",
    ]),
    ("MIDDLE EAST", RED, [
        "Gaza strikes kill UNRWA worker, Hamas chief",
        "Iran refuses talks until 7 conditions met",
        "Qatar PM seeks to revive US-Iran talks",
        "Netanyahu presses Trump on Iran strikes",
        "Iraq takes over Kurdish oilfields",
        "Yemen strikes kill about 25, Houthis say",
    ]),
    ("AMERICAS", TEAL, [
        "Democrats win House by widest margin",
        "Trump to speed up federal death sentences",
        "Oregon, Virginia sue SpaceX over Grok",
        "Car bomb hits governor's office, Colombia",
        "Mexico to try 'Chapo Isidro' despite US",
        "Measles claims ninth life in Pennsylvania",
    ]),
    ("ASIA", GOLD, [
        "S. Korea: $375,000 to catch AI exam cheats",
        "Russian jets enter S. Korea defence zone",
        "Pakistan astronaut to fly on China station",
        "Nepal hit by 5.6 quake near China border",
        "Indonesia factory fire kills 26",
        "Malaysia to return 6,500 Rohingya",
    ]),
    ("AFRICA", (120, 70, 20), [
        "UN seeks probe into Benghazi port attacks",
        "Fighting traps Ebola teams in DR Congo",
        "DR Congo says military aircraft missing",
        "Somalia, Uganda step up anti-Shabaab fight",
        "Solomon Islands ends China security pact",
        "DR Congo rebels claim shootdown",
    ]),
    ("GLOBAL", GREY, [
        "14 nations back ICJ Rohingya ruling",
        "UN chief: AI risk framework in a year",
        "UK sanctions Myanmar generals",
        "NATO chief vows space defence",
        "Spain court amnesties Puigdemont",
        "COP31 collapse divides the world",
    ]),
]
col_w = (W - 2 * M - 10) // 3
row_h = 168
for idx, (name, col, stories) in enumerate(REGIONS):
    cx0 = M + (idx % 3) * (col_w + 5)
    cy0 = 458 + (idx // 3) * (row_h + 8)
    lf = font(F_SANS_B, 12)
    lw = int(d.textlength(name, font=lf)) + 14
    d.rectangle([cx0, cy0, cx0 + lw, cy0 + 20], fill=col)
    d.text((cx0 + 7, cy0 + 2), name, font=lf, fill=PAPER)
    yy = cy0 + 30
    for st in stories:
        d.ellipse([cx0 + 2, yy + 5, cx0 + 7, yy + 10], fill=col)
        d.text((cx0 + 12, yy), st, font=font(F_SANS, 13), fill=INK)
        yy += 21

# ---- Footer: map strip + credit ----
fy = 458 + 2 * (row_h + 8) + 10
hline(d, M, W - M, fy, INK, 2)
d.text((M, fy + 10), "THE WORLD, 24 NOVEMBER 2026", font=font(F_SANS_B, 13), fill=INK)
# tiny world map: dots on a rough world outline (deterministic)
random.seed(24)
d.rectangle([M, fy + 36, W - M, fy + 118], fill=(214, 228, 240))
for _ in range(420):
    px = random.randint(M + 6, W - M - 6)
    py = random.randint(fy + 40, fy + 114)
    # keep dots inside a rough landmass band (skip the ocean gaps)
    if 300 < px < 420 and py > fy + 84:
        continue
    d.ellipse([px, py, px + 2, py + 2], fill=BLUE)
d.text((M, fy + 126), "Every story above was reported on 24 November 2026.",
       font=font(F_SANS, 12), fill=GREY)
d.text((W - M - 210, fy + 126), "Drawn by an AI agent, no network.",
       font=font(F_SANS, 12), fill=GREY)

path = os.path.join(OUT, "entry.png")
img.save(path, "PNG")
h = hashlib.sha256(open(path, "rb").read()).hexdigest()
print(f"wrote {path} sha256={h} size={img.size}")
