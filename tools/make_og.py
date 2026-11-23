#!/usr/bin/env python3
"""og.jpg (1200x630): paper ground, the name in Helvetica Neue Bold, B&W photo on the right. Needs Pillow."""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAPER, INK, MUTE = (236, 235, 230), (20, 20, 20), (116, 113, 106)
og = Image.new("RGB", (1200, 630), PAPER)
ph = Image.open(ROOT / "img/decks-bw-1200.jpg").convert("L").convert("RGB")
w = 470
ph = ph.resize((w, int(ph.height * w / ph.width)), Image.LANCZOS)
top = int((ph.height - 630) * 0.4)
og.paste(ph.crop((0, top, w, top + 630)), (1200 - w, 0))
d = ImageDraw.Draw(og)
bold = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 132, index=1)
reg = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 30, index=0)
mono = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 19)
d.text((60, 170), "CARLO DE MARCHIS · SELECTOR · TORINO", font=mono, fill=MUTE)
x = 56
for ch in "selectazzz":  # tight tracking, like the page
    d.text((x, 200), ch, font=bold, fill=INK)
    x += d.textlength(ch, font=bold) - 7
for i, line in enumerate(["Spiritual jazz, nu-jazz, house and world music.",
                          "Mostly vinyl, now hybrid."]):
    d.text((62, 390 + i * 42), line, font=reg, fill=INK)
d.text((62, 520), "SELECTAZZZ.CARLODEMARCHIS.IT", font=mono, fill=MUTE)
og.save(ROOT / "og.jpg", quality=88)
print("og.jpg", og.size)
