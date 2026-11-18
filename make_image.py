#!/usr/bin/env python3
"""Compose the news-image entry: a one-page newspaper front page summing up
world news of Wednesday 18 November 2026, as a 1024x1024 PNG.

Every word on the page comes from the verified brief in
../news-brief.md (researched 2026-11-19 from multiple news sources).
Text is drawn with PIL + DejaVu fonts, so every headline is real,
readable text -- never text-to-image output.

Layout (1024x1024, paper background, black ink, red accent):
  masthead "WORLD NEWS" + date line
  lead story: Gulf escalation (US strikes Iran, Iran hits back)
  grid: Crimea bridge, Shenzhen summit, US Senate, Ebola, measles
  "Also in brief" box + footer with the date again
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (250, 246, 236)      # warm newsprint
INK = (17, 17, 17)
RED = (158, 27, 27)
MUTED = (85, 85, 85)
RULE = (17, 17, 17)
LIGHT_RULE = (150, 145, 130)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def hrule(draw, x0, x1, y, width=2, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def block_height(draw, w, headline, summary, head_size=28):
    """Pixel height of a story block (kicker + headline + summary)."""
    h = 28  # kicker
    h += len(wrap(draw, headline, SERIF_B(head_size), w)) * int(head_size * 1.12)
    h += 4
    h += len(wrap(draw, summary, SANS(19), w)) * 24
    return h


def story_block(draw, x, y, w, kicker, headline, summary, head_size=28):
    """One grid story: red kicker, bold serif headline, one-line summary.
    Returns the y just below the block."""
    draw.text((x, y), kicker, font=SANS_B(19), fill=RED)
    y += 28
    y = draw_wrapped(draw, x, y, headline, SERIF_B(head_size),
                     w, leading=int(head_size * 1.12))
    y += 4
    y = draw_wrapped(draw, x, y, summary, SANS(19), w, leading=24)
    return y


def build(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 34                      # side margin
    CW = W - 2 * MX              # content width = 956

    # ---- masthead ------------------------------------------------------
    y = 22
    title = "WORLD NEWS"
    tf = SERIF_B(88)
    d.text(((W - d.textlength(title, font=tf)) / 2, y), title,
           font=tf, fill=INK)
    y = 122
    date_line = "WEDNESDAY, 18 NOVEMBER 2026"
    df = SANS_B(27)
    # light letter-spacing by drawing with extra gaps
    d.text(((W - d.textlength(date_line, font=df)) / 2, y), date_line,
           font=df, fill=RED)
    y = 166
    hrule(d, MX, W - MX, y, width=4)
    hrule(d, MX, W - MX, y + 7, width=1)
    y = 188

    # ---- lead story: Gulf escalation -----------------------------------
    d.text((MX, y), "GULF ESCALATION  —  LEAD STORY",
           font=SANS_B(23), fill=RED)
    y += 32
    y = draw_wrapped(d, MX, y,
                     "U.S. STRIKES IRAN, TEHRAN HITS BACK",
                     SERIF_B(56), CW, leading=62)
    y += 6
    y = draw_wrapped(
        d, MX, y,
        "American jets struck a Revolutionary Guard missile site on Qeshm "
        "Island. Iran fired drones and missiles at Bahrain and Kuwait, hit "
        "U.S. Patriot defences, shot down an MQ-9 drone; Houthi drones hit "
        "Saudi pipeline stations.",
        SANS(24), CW, leading=30)
    y += 22
    hrule(d, MX, W - MX, y, width=2)

    # ---- grid of five more stories ------------------------------------
    # Rows are placed by measured height, so no block can overlap the next.
    col_w = (CW - 22) // 2
    x2 = MX + col_w + 22
    gy = y + 14
    GAP = 14

    rows = [
        (("UKRAINE", "Ukraine Hits Crimea Bridge Again",
          "Drones and missiles strike the Kerch Bridge a second day; "
          "a road span falls into the strait."),
         ("SUMMIT IN SHENZHEN", "Trump, Xi and Putin Meet in China",
          "Xi and Putin meet ahead of Thursday's trilateral summit; "
          "Xi vows to resist trade protectionism.")),
        (("U.S. POLITICS", "Democrats Take the Senate, 56–44",
          "Mary Peltola defeats Dan Sullivan in Alaska; Democrats "
          "projected to a 56–44 majority."),
         ("HEALTH — AFRICA", "Ebola Surges in DR Congo",
          "Outbreak more than doubles in three months: 11,000+ cases, "
          "5,400+ deaths, the UN says.")),
        (("HEALTH — AMERICA", "U.S. Loses Measles-Free Status",
          "After 26 years: 5,400+ cases, 10 deaths — the first measles "
          "deaths since the early 1990s."),
         None),
    ]
    for i, (left, right) in enumerate(rows):
        h_left = block_height(d, col_w, left[1], left[2])
        h_right = block_height(d, col_w, right[1], right[2]) if right else 0
        row_h = max(h_left, h_right, 140)
        story_block(d, MX, gy, col_w, *left)
        if right:
            story_block(d, x2, gy, col_w, *right)
        else:
            # "Also in brief" box fills the right column of the last row.
            bx, by = x2, gy
            d.rectangle([bx, by, bx + col_w, by + 138], outline=RULE, width=2)
            d.text((bx + 14, by + 10), "ALSO IN BRIEF",
                   font=SANS_B(19), fill=RED)
            draw_wrapped(d, bx + 14, by + 40,
                         "Cyclone Xavier slams the Cook Islands. Nvidia "
                         "revenue doubles. COP31 talks deadlocked. Russian "
                         "plane crash kills 19 in Siberia.",
                         SANS(19), col_w - 28, leading=25)
        gy += row_h + GAP
        if i < len(rows) - 1:
            hrule(d, MX, W - MX, gy - 8, width=1, fill=LIGHT_RULE)

    # ---- footer ---------------------------------------------------------
    hrule(d, MX, W - MX, gy - 2, width=4)
    foot = "WORLD NEWS — WEDNESDAY 18 NOVEMBER 2026  •  THE DAY'S WORLD NEWS, ONE PAGE"
    ff = SANS_B(17)
    d.text(((W - d.textlength(foot, font=ff)) / 2, gy + 8), foot,
           font=ff, fill=MUTED)

    img.save(path, "PNG", optimize=True)
    return path


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    build(out)
    print("wrote", out, os.path.getsize(out), "bytes")
