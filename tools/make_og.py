#!/usr/bin/env python3
"""Generates assets/img/og.png (1200x630 social share image). Requires Pillow."""
import math, os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
img = Image.new("RGB", (W, H), "#0b1530"); px = img.load()
for y in range(H):
    for x in range(W):
        a = max(0, 1 - math.hypot(x - 200, y - 120) / 500) * .45
        c = max(0, 1 - math.hypot(x - 1050, y - 80) / 520) * .35
        px[x, y] = (min(255, int(11 + 9 * a + 128 * c)), min(255, int(21 + 203 * a + 71 * c)), min(255, int(48 + 148 * a + 198 * c)))
d = ImageDraw.Draw(img)
def font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default()
d.rounded_rectangle((80, 90, 170, 180), radius=24, fill="#14e0c4")
d.polygon([(135, 102), (100, 142), (124, 142), (117, 170), (152, 128), (130, 128)], fill="#0b1530")
d.text((195, 100), "Smart.Supply", font=font(64), fill="white")
d.text((80, 250), "Source smarter.", font=font(78), fill="white")
d.text((80, 345), "Ship cheaper. Decide faster.", font=font(56), fill="#b8f35a")
d.text((80, 470), "Free RFQs  •  Vetted suppliers  •  9 pro calculators  •  Guides", font=font(30), fill="#c5cee6")
img.save(os.path.join(ROOT, "assets", "img", "og.png"), optimize=True)
print("og.png written")
