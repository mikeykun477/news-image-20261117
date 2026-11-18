"""Lay out the 1024x1024 front page for Tuesday 17 November 2026.

Build-time helper only: the entry program (``main.py``) never runs this
file. It reads the hero photograph already stored in this folder,
arranges the masthead, the lead story, six story tiles and the
also-today strip on a single page, and saves the result as
``entry.png``. Run it again any time the layout changes:

    python3 compose.py [output-path]

With no argument the finished page is written next to this script.
Needs Pillow, which is a build-time dependency only.
"""

import sys
import textwrap

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
HERO_FILE = "media-generation-news-hero-17nov-0-2776fce9-aa0b-4c85-b174-227a535085ab.png"
RESULT_FILE = "entry.png"

PAPER = (247, 243, 232)      # warm off-white page
INK = (26, 26, 26)           # near-black body text
NAVY = (15, 42, 68)          # masthead band and tile rules
GOLD = (198, 154, 66)        # thin rules under masthead and hero
CRIMSON = (163, 22, 33)      # lead headline and kickers
GREY = (102, 102, 102)       # tile decks
TILE_FILL = (252, 250, 244)  # slightly lighter tile face
TILE_EDGE = (178, 172, 158)  # tile outline
WHITE = (255, 255, 255)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF = FONT_DIR / "DejaVuSerif.ttf"
SERIF_BOLD = FONT_DIR / "DejaVuSerif-Bold.ttf"
SANS = FONT_DIR / "DejaVuSans.ttf"
SANS_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"

LEAD_HEADLINE = "US AND IRAN TRADE FIRE"
LEAD_DECK = (
    "US strikes a missile site on Qeshm Island; Iran fires drones "
    "at a US radar base in Bahrain \u2014 the third attack in five days."
)

TILES = [
    (
        "UKRAINE",
        "Kerch Bridge hit again",
        "A road section falls into the strait on the second day of "
        "strikes. Russia hits bridges in Kyiv in reply.",
    ),
    (
        "NVIDIA",
        "Record $115bn quarter",
        "Revenue tops $115 billion \u2014 but the chip giant will not "
        "bring back ousted chief Jensen Huang.",
    ),
    (
        "ASIA",
        "Trump heads to APEC",
        "President travels to Shenzhen; nuclear talks with Xi Jinping "
        "and Putin are planned.",
    ),
    (
        "GAZA",
        "Four allies press Israel",
        "UK, Australia, Canada and Italy urge crossings opened for aid "
        "as the situation turns catastrophic.",
    ),
    (
        "JAPAN",
        "Jets scramble in the north",
        "Fighters scrambled after suspected Russian aircraft enter "
        "Japanese airspace.",
    ),
    (
        "YEMEN",
        "Houthis advance on Aden",
        "Government forces pull back from the Red Sea coast as rebels "
        "push south.",
    ),
]

STRIP_TEXT = (
    "Depardieu admits a sex-assault charge in Paris \u2022 Ebola in DR "
    "Congo passes 11,000 cases \u2022 US loses measles elimination "
    "status after 26 years \u2022 Nepal first to get UN loss-and-damage "
    "funds after floods \u2022 Five EU states plan a migrant return hub "
    "in Rwanda."
)


def _typeface(path, size):
    """Load one TrueType face, falling back to Pillow's built-in font."""
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def _fit_lines(draw, text, font, width):
    """Break a paragraph into lines that fit inside ``width`` pixels."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if draw.textlength(trial, font=font) <= width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def _spaced_line(draw, text, font, centre_x, top, fill, gap=7):
    """Draw one line with extra space between its letters."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + gap * (len(text) - 1)
    x = centre_x - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, top), ch, font=font, fill=fill)
        x += w + gap


def _cover_crop(photo, width, height, focus=0.42):
    """Scale a photo to cover a box, cropping the excess vertically."""
    scaled = photo.resize(
        (width, round(photo.height * width / photo.width)),
        Image.LANCZOS,
    )
    if scaled.height <= height:
        return scaled
    spare = scaled.height - height
    top = round(spare * focus)
    return scaled.crop((0, top, width, top + height))


def _paint_masthead(draw):
    """Navy band with the paper name over the date."""
    draw.rectangle([0, 0, PAGE, 108], fill=NAVY)
    eyebrow = _typeface(SANS_BOLD, 21)
    _spaced_line(
        draw, "THE WORLD IN ONE IMAGE", eyebrow, PAGE // 2, 16, GOLD
    )
    dateline = _typeface(SERIF_BOLD, 52)
    draw.text(
        (PAGE // 2, 46),
        "TUESDAY 17 NOVEMBER 2026",
        font=dateline,
        fill=WHITE,
        anchor="ma",
    )
    draw.rectangle([0, 104, PAGE, 108], fill=GOLD)


def _paint_lead(draw):
    """Centred lead headline and its two-line deck."""
    headline = _typeface(SERIF_BOLD, 50)
    draw.text(
        (PAGE // 2, 386),
        LEAD_HEADLINE,
        font=headline,
        fill=CRIMSON,
        anchor="ma",
    )
    deck_font = _typeface(SANS, 23)
    rows = _fit_lines(draw, LEAD_DECK, deck_font, 940)
    y = 448
    for row in rows:
        draw.text((PAGE // 2, y), row, font=deck_font, fill=INK, anchor="ma")
        y += 32


def _paint_tile(draw, box, kicker, headline, deck):
    """One bordered story tile: kicker, headline, short deck."""
    left, top, right, bottom = box
    draw.rectangle([left, top, right, bottom], fill=TILE_FILL,
                   outline=TILE_EDGE, width=1)
    draw.rectangle([left, top, right, top + 5], fill=NAVY)
    kick_font = _typeface(SANS_BOLD, 17)
    draw.text((left + 14, top + 16), kicker, font=kick_font, fill=CRIMSON)
    head_font = _typeface(SERIF_BOLD, 27)
    rows = _fit_lines(draw, headline, head_font, right - left - 28)
    y = top + 44
    for row in rows:
        draw.text((left + 14, y), row, font=head_font, fill=INK)
        y += 33
    deck_font = _typeface(SANS, 16)
    y += 4
    for row in _fit_lines(draw, deck, deck_font, right - left - 28):
        draw.text((left + 14, y), row, font=deck_font, fill=GREY)
        y += 22


def _paint_tiles(draw):
    """Six tiles in a three-across, two-down grid."""
    margin = 24
    gap = 14
    width = (PAGE - 2 * margin - 2 * gap) // 3
    height = 186
    for index, (kicker, headline, deck) in enumerate(TILES):
        col = index % 3
        row = index // 3
        left = margin + col * (width + gap)
        top = 556 + row * (height + 12)
        _paint_tile(draw, (left, top, left + width, top + height),
                    kicker, headline, deck)


def _paint_strip(draw):
    """Gold-ruled also-today strip along the bottom of the page."""
    draw.rectangle([0, 946, PAGE, 950], fill=GOLD)
    label_font = _typeface(SANS_BOLD, 18)
    draw.text((24, 956), "ALSO TODAY", font=label_font, fill=CRIMSON)
    body_font = _typeface(SANS, 15)
    rows = _fit_lines(draw, STRIP_TEXT, body_font, PAGE - 48)
    y = 980
    for row in rows:
        draw.text((24, y), row, font=body_font, fill=INK)
        y += 20


def _assemble_page(here):
    """Compose every section onto a fresh blank page."""
    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(page)
    _paint_masthead(draw)
    with Image.open(here / HERO_FILE) as photo:
        hero = _cover_crop(photo.convert("RGB"), PAGE, 256)
    page.paste(hero, (0, 108))
    draw.rectangle([0, 364, PAGE, 368], fill=GOLD)
    _paint_lead(draw)
    _paint_tiles(draw)
    _paint_strip(draw)
    return page


def _main(argv):
    here = Path(__file__).resolve().parent
    target = Path(argv[1]) if len(argv) > 1 else here / RESULT_FILE
    page = _assemble_page(here)
    page.save(target, format="PNG")
    print(f"Wrote {target} ({page.width}x{page.height})")


if __name__ == "__main__":
    _main(sys.argv)
