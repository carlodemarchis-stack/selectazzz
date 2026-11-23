#!/usr/bin/env python3
"""og.jpg (1200x630) in the Tono theme: darkened photo, "selectazzz" in Righteous (OFL, fetched
from google/fonts into tools/.cache), "with Carlo De Marchis" in Helvetica Neue Bold, genres in
yellow-cream capitals. Needs Pillow."""
import pathlib, urllib.request
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools/.cache"; CACHE.mkdir(exist_ok=True)
RIGHTEOUS = CACHE / "Righteous-Regular.ttf"
if not RIGHTEOUS.exists():
    urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/righteous/Righteous-Regular.ttf", RIGHTEOUS)
CREAM, YELLOW, WHITE = (243, 230, 196), (239, 226, 162), (255, 248, 234)

ph = Image.open(ROOT / "img/decks-bw-1200.jpg").convert("RGB")
ph = ph.resize((1200, int(ph.height * 1200 / ph.width)), Image.LANCZOS)
top = int((ph.height - 630) * 0.3)
og = ph.crop((0, top, 1200, top + 630))
og = ImageEnhance.Brightness(og).enhance(0.38)
og = Image.blend(og, Image.new("RGB", og.size, (60, 45, 30)), 0.18)
d = ImageDraw.Draw(og)

def centred(text, font, y, fill, shadow=True):
    w = d.textlength(text, font=font)
    if shadow:
        sh = Image.new("RGBA", og.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text(((1200 - w) / 2, y + 4), text, font=font, fill=(0, 0, 0, 150))
        og.paste(sh.filter(ImageFilter.GaussianBlur(8)), (0, 0), sh.filter(ImageFilter.GaussianBlur(8)))
    d.text(((1200 - w) / 2, y), text, font=font, fill=fill)

centred("selectazzz", ImageFont.truetype(str(RIGHTEOUS), 190), 95, CREAM)
centred("with Carlo De Marchis", ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 58, index=1), 330, WHITE)
caps = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 30, index=1)
centred("SPIRITUAL JAZZ, NU-JAZZ, FUNK, SOUL, HOUSE", caps, 440, YELLOW)
centred("MOSTLY VINYL, NOW HYBRID · TORINO", caps, 482, YELLOW)
og.save(ROOT / "og.jpg", quality=88)
print("og.jpg", og.size)
