"""Gera os ícones e a imagem de compartilhamento a partir de assets/logo.svg.

Só precisa rodar de novo se trocar o logo:  python3 gerar_imagens.py
(precisa de: pip install cairosvg pillow)
"""
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

A = Path(__file__).parent / "assets"
svg = (A / "logo.svg").read_bytes()

for nome, tam in [("favicon-32.png", 32), ("apple-touch-icon.png", 180), ("logo-512.png", 512)]:
    cairosvg.svg2png(bytestring=svg, write_to=str(A / nome), output_width=tam, output_height=tam)

# Imagem de compartilhamento 1200x630 (WhatsApp, Facebook, Google)
W, H = 1200, 630
img = Image.new("RGB", (W, H), "#06065F")
d = ImageDraw.Draw(img)
for y in range(H):  # degradê azul
    t = y / H
    r = int(10 + (4 - 10) * t)
    g = int(10 + (4 - 10) * t)
    b = int(184 + (61 - 184) * t)
    d.line([(0, y), (W, y)], fill=(r, g, b))
brilho = Image.new("L", (W, H), 0)
ImageDraw.Draw(brilho).ellipse([760, 420, 1460, 900], fill=80)
brilho = brilho.filter(ImageFilter.GaussianBlur(120))
img.paste(Image.new("RGB", (W, H), "#FFC61A"), (0, 0), brilho)

logo = Image.open(A / "logo-512.png").convert("RGBA").resize((220, 220), Image.LANCZOS)
img.paste(logo, (80, 80), logo)

F = "/usr/share/fonts/opentype/inter/"
bold = ImageFont.truetype(F + "Inter-ExtraBold.otf", 76)
semi = ImageFont.truetype(F + "Inter-SemiBold.otf", 34)
d = ImageDraw.Draw(img)
d.text((80, 340), "Piscicultura", font=bold, fill="#FFFFFF")
d.text((80, 425), "Lucrativa", font=bold, fill="#FFC61A")
d.text((80, 530), "Hub nacional de pisciculturas · 20% só sobre vendas", font=semi, fill="#E6E6FF")
img.save(A / "og-capa.png", optimize=True)
print("ok")
