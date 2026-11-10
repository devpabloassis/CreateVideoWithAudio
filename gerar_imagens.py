"""Gera 3 imagens de fundo de exemplo em imgs/ (fundo1.jpg, fundo2.jpg, fundo3.jpg).

Você pode substituir essas imagens pelas suas (qualquer .jpg/.png dentro de imgs/).
"""
import os
import random

from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_IMGS = os.path.join(BASE_DIR, "imgs")
LARGURA, ALTURA = 1280, 720

PALETAS = [
    ((255, 94, 98), (255, 195, 113)),   # pôr do sol
    ((54, 209, 220), (91, 134, 229)),   # céu/mar
    ((142, 45, 226), (74, 0, 224)),     # roxo
]


def gradiente(cor1, cor2):
    img = Image.new("RGB", (LARGURA, ALTURA))
    draw = ImageDraw.Draw(img)
    for y in range(ALTURA):
        p = y / (ALTURA - 1)
        cor = tuple(int(a + (b - a) * p) for a, b in zip(cor1, cor2))
        draw.line([(0, y), (LARGURA, y)], fill=cor)
    return img


def decorar(img, semente):
    rnd = random.Random(semente)
    camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(camada)
    for _ in range(25):
        r = rnd.randint(30, 160)
        x, y = rnd.randint(0, LARGURA), rnd.randint(0, ALTURA)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, rnd.randint(15, 45)))
    camada = camada.filter(ImageFilter.GaussianBlur(6))
    return Image.alpha_composite(img.convert("RGBA"), camada).convert("RGB")


def main():
    os.makedirs(PASTA_IMGS, exist_ok=True)
    for i, (c1, c2) in enumerate(PALETAS, start=1):
        caminho = os.path.join(PASTA_IMGS, f"fundo{i}.jpg")
        decorar(gradiente(c1, c2), i).save(caminho, quality=92)
        print(f"Imagem criada: {caminho}")


if __name__ == "__main__":
    main()
