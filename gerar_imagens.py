"""Gera os ícones e a imagem de compartilhamento a partir de fonte/logo.png.

Só precisa rodar de novo se trocar o logo:  python3 gerar_imagens.py
(precisa de: pip install pillow)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

A = Path(__file__).parent / "assets"
logo_fonte = Image.open(Path(__file__).parent / "fonte" / "logo.png").convert("RGBA")
for nome, tam in [("favicon-32.png", 32), ("logo-512.png", 512)]:
    logo_fonte.resize((tam, tam), Image.LANCZOS).save(A / nome)
logo_fonte.resize((112, 112), Image.LANCZOS).save(A / "logo-112.webp", quality=90)
apple = Image.new("RGB", (180, 180), "white")
pequeno = logo_fonte.resize((180, 180), Image.LANCZOS)
apple.paste(pequeno, (0, 0), pequeno)
apple.save(A / "apple-touch-icon.png")

# Imagem de compartilhamento 1200x630 (WhatsApp, Facebook, Google)
W, H = 1200, 630
img = Image.new("RGB", (W, H), "#06065F")
d = ImageDraw.Draw(img)
A0, A1 = (0, 0, 179), (255, 198, 26)  # mesmo degradê do topo do site
for x in range(0, W + H, 2):
    t = min(1, x / (W + H))
    cor = tuple(int(A0[i] + (A1[i] - A0[i]) * t) for i in range(3))
    d.line([(x, 0), (x - H, H)], fill=cor, width=3)
sombra = Image.new("L", (W, H), 0)
ImageDraw.Draw(sombra).rectangle([0, 300, 900, H], fill=150)
sombra = sombra.filter(ImageFilter.GaussianBlur(140))
img.paste(Image.new("RGB", (W, H), "#00004D"), (0, 0), sombra)

logo = logo_fonte.resize((220, 220), Image.LANCZOS)
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
