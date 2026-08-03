#!/usr/bin/env python3
"""Gera os ícones do PWA no tema editorial: fundo creme, "D&D" em tinta com o
& dourado, fio dourado e a data em Cormorant.

Uso:  python3 tools/gerar-icones.py
Requer Pillow. Baixa Playfair Display e Cormorant Garamond do Google Fonts para
um diretório temporário (as fontes não são versionadas — pesam ~1,4 MB).
"""
import os
import tempfile
import urllib.request

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CREME = (244, 239, 231)   # --bg do tema claro
TINTA = (42, 36, 29)      # --ink
OURO = (184, 147, 90)     # --gold
FIO = (206, 180, 138)     # dourado mais claro, pro fio não competir com o &

FONTES = {
    "Playfair.ttf": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
    "Cormorant.ttf": "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf",
}


def baixar_fontes(destino):
    caminhos = {}
    for nome, url in FONTES.items():
        alvo = os.path.join(destino, nome)
        if not os.path.exists(alvo):
            print("baixando", nome, "…")
            urllib.request.urlretrieve(url, alvo)
        caminhos[nome] = alvo
    return caminhos


def fonte(path, size, peso):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([peso])   # fontes variáveis: eixo wght
    except Exception:
        pass
    return f


def largura(d, txt, f):
    a = d.textbbox((0, 0), txt, font=f)
    return a[2] - a[0]


def desenhar(S, fontes):
    img = Image.new("RGB", (S, S), CREME)
    d = ImageDraw.Draw(img)
    k = S / 512.0

    f_letra = fonte(fontes["Playfair.ttf"], int(170 * k), 600)
    f_data = fonte(fontes["Cormorant.ttf"], int(56 * k), 600)

    y = S / 2 - 30 * k
    wD = largura(d, "D", f_letra)
    wA = largura(d, "&", f_letra)
    esp = 12 * k
    x = S / 2 - (wD * 2 + wA + esp * 2) / 2

    d.text((x, y), "D", font=f_letra, fill=TINTA, anchor="lm")
    d.text((x + wD + esp, y), "&", font=f_letra, fill=OURO, anchor="lm")
    d.text((x + wD + esp + wA + esp, y), "D", font=f_letra, fill=TINTA, anchor="lm")

    fio_y = y + 105 * k
    d.rectangle([S / 2 - 80 * k, fio_y, S / 2 + 80 * k, fio_y + max(1, 3 * k)], fill=FIO)
    d.text((S / 2, y + 160 * k), "16 · 10 · 27", font=f_data, fill=OURO, anchor="mm")
    return img


def main():
    with tempfile.TemporaryDirectory() as tmp:
        fontes = baixar_fontes(tmp)
        for nome, tam in [("icon-512.png", 512), ("icon-192.png", 192), ("apple-touch-icon.png", 180)]:
            # renderiza em 4x e reduz: a tipografia fica bem mais limpa
            img = desenhar(tam * 4, fontes).resize((tam, tam), Image.LANCZOS)
            caminho = os.path.join(RAIZ, nome)
            img.save(caminho, "PNG", optimize=True)
            print("ok:", nome, "->", os.path.getsize(caminho), "bytes")
    print("\nLembre de subir a versão do CACHE no sw.js — os ícones têm nome fixo.")


if __name__ == "__main__":
    main()
