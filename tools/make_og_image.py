"""OGP画像 docs/assets/og-image.jpg (1200x630) を assets/hero.jpg から生成する。"""
import os
from PIL import Image, ImageDraw, ImageFont

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'assets')
im = Image.open(os.path.join(A, 'hero.jpg')).convert('RGB')
w = 1200
im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
top = (im.height - 630) // 2
im = im.crop((0, top, w, top + 630))

d = ImageDraw.Draw(im, 'RGBA')
d.rectangle((0, 0, w, 630), fill=(42, 38, 34, 70))
font_b = ImageFont.truetype('C:/Windows/Fonts/YuGothB.ttc', 112)
font_s = ImageFont.truetype('C:/Windows/Fonts/YuGothB.ttc', 40)
# カード
x0, y0, x1, y1 = 120, 190, 1080, 440
d.rounded_rectangle((x0 + 8, y0 + 8, x1 + 8, y1 + 8), 36, fill=(42, 38, 34, 255))
d.rounded_rectangle((x0, y0, x1, y1), 36, fill=(255, 248, 236, 255), outline=(42, 38, 34, 255), width=5)
t1, t2 = '宅配食', 'ナビ'
wa = d.textlength(t1, font=font_b); wb = d.textlength(t2, font=font_b)
sx = (w - (wa + wb + 20)) / 2
d.text((sx, 215), t1, font=font_b, fill=(42, 38, 34, 255))
d.rounded_rectangle((sx + wa + 8, 228, sx + wa + wb + 36, 350), 24, fill=(217, 63, 36, 255))
d.text((sx + wa + 22, 215), t2, font=font_b, fill=(255, 255, 255, 255))
sub = 'ミールキット・宅配弁当を目的別に比較'
d.text(((w - d.textlength(sub, font=font_s)) / 2, 365), sub, font=font_s, fill=(106, 95, 85, 255))
out = os.path.join(A, 'og-image.jpg')
im.save(out, quality=84, optimize=True)
print(out, os.path.getsize(out))
