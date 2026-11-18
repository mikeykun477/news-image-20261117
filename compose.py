#!/usr/bin/env python3
"""Compose the 17 Nov 2026 front-page image (build-time tool only).

Reads the generated hero illustration, lays out a newspaper front page with
crisp PIL-rendered headlines for the day's verified stories, writes entry.png
(1024x1024, under 1 MiB). Run:  python3 compose.py
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1024, 1024
PAPER = (247, 242, 232)
NAVY = (16, 36, 60)
GOLD = (212, 160, 60)
RED = (176, 32, 32)
INK = (24, 24, 24)
GREY = (96, 92, 84)
RULE = (186, 178, 160)
WHITE = (255, 255, 255)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

HERO = "media-generation-news-hero-17nov-0-2776fce9-aa0b-4c85-b174-227a535085ab.png"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def centered(d, cx, y, text, fnt, fill):
    d.text((cx - d.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size


def para(d, x, y, text, fnt, fill, max_w, leading):
    for line in wrap(d, text, fnt, max_w):
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---- Masthead ----
d.rectangle([0, 0, W, 100], fill=NAVY)
d.rectangle([0, 100, W, 104], fill=GOLD)
centered(d, W // 2, 12, "T H E   W O R L D   I N   O N E   I M A G E",
         font(SANS_B, 19), GOLD)
centered(d, W // 2, 38, "TUESDAY 17 NOVEMBER 2026",
         font(SERIF_B, 46), WHITE)

# ---- Hero (lead visual: bridge + jets + island) ----
hero = Image.open(HERO).convert("RGB")
hero = ImageOps.fit(hero, (W, 296), method=Image.LANCZOS, centering=(0.5, 0.12))
img.paste(hero, (0, 104))
d.rectangle([0, 400, W, 404], fill=GOLD)

# ---- Lead headline + deck ----
y = 418
centered(d, W // 2, y, "US AND IRAN TRADE FIRE",
         font(SERIF_B, 47), RED)
y = 478
centered(d, W // 2, y,
         "US strikes a missile site on Qeshm Island; Iran fires drones",
         font(SANS, 22), INK)
centered(d, W // 2, y + 28,
         "at a US radar base in Bahrain \u2014 the third attack in five days.",
         font(SANS, 22), INK)

# ---- Story grid: 3 columns x 2 rows ----
TILES = [
    ("UKRAINE", "Kerch Bridge hit again",
     "A road section falls into the strait on the second day of strikes. Russia hits bridges in Kyiv in reply."),
    ("NVIDIA", "Record $115bn quarter",
     "Revenue tops $115 billion \u2014 but the chip giant will not bring back ousted chief Jensen Huang."),
    ("ASIA", "Trump heads to APEC",
     "President travels to Shenzhen; nuclear talks with Xi Jinping and Putin are planned."),
    ("GAZA", "Four allies press Israel",
     "UK, Australia, Canada and Italy urge crossings opened for aid as the situation turns catastrophic."),
    ("JAPAN", "Jets scramble in the north",
     "Fighters scrambled after suspected Russian aircraft enter Japanese airspace."),
    ("YEMEN", "Houthis advance on Aden",
     "Government forces pull back from the Red Sea coast as rebels push south."),
]
gx, gy = 24, 556
cw, ch, gap = 318, 178, 12
for i, (kicker, head, deck) in enumerate(TILES):
    x = gx + (i % 3) * (cw + gap)
    yy = gy + (i // 3) * (ch + gap)
    d.rectangle([x, yy, x + cw, yy + ch], outline=RULE, width=2)
    d.rectangle([x, yy, x + cw, yy + 4], fill=NAVY)
    d.text((x + 14, yy + 14), kicker, font=font(SANS_B, 17), fill=RED)
    ty = para(d, x + 14, yy + 40, head, font(SERIF_B, 23), INK,
              cw - 28, 28)
    para(d, x + 14, ty + 4, deck, font(SANS, 16), GREY, cw - 28, 21)

# ---- Also today strip ----
y = 936
d.rectangle([0, y, W, y + 2], fill=GOLD)
d.text((24, y + 10), "ALSO TODAY", font=font(SANS_B, 17), fill=RED)
para(d, 24, y + 34,
     "Depardieu admits a sex-assault charge in Paris  \u2022  Ebola in DR Congo passes 11,000 cases  \u2022  "
     "US loses measles elimination status after 26 years  \u2022  Nepal first to get UN loss-and-damage funds "
     "after floods  \u2022  Five EU states plan a migrant return hub in Rwanda.",
     font(SANS, 15), INK, W - 48, 19)

img.save("entry.png", optimize=True)
print("wrote entry.png", img.size)
