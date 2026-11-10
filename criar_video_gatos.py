"""Cria um vídeo MP4 com curiosidades sobre gatos da API catfact.ninja.

Fluxo:
  1. Chama a API 4 vezes (https://catfact.ninja/fact).
  2. Para cada mensagem gera um áudio (gTTS, em inglês).
  3. Para cada mensagem escolhe aleatoriamente uma das imagens de imgs/ e escreve o texto nela.
  4. Cada cena dura o tempo do seu áudio; ao final junta tudo em output/video_gatos_<data>.mp4.

Uso:
  python criar_video_gatos.py [--quantidade 4] [--saida output/meu_video.mp4]
"""
import argparse
import glob
import os
import random
import sys
import time
from datetime import datetime

import numpy as np
import requests
from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URL_API = "https://catfact.ninja/fact"
TAMANHO_MAX = 250      # caracteres; mensagens maiores não cabem bem na tela
PASTA_IMGS = os.path.join(BASE_DIR, "imgs")
PASTA_SAIDA = os.path.join(BASE_DIR, "output")
PASTA_TEMP = os.path.join(PASTA_SAIDA, "temp")

LARGURA, ALTURA = 1280, 720
FPS = 24
PAUSA_FINAL = 1.0      # segundos extras de imagem depois que o áudio termina
IDIOMA_VOZ = "en"      # as mensagens da API são em inglês

FONTES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]


# ---------------------------------------------------------------- API

def buscar_mensagem(tentativas=3):
    """Retorna o texto de uma curiosidade sobre gatos. A API responde {"fact": "...", "length": N}."""
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.get(URL_API, params={"max_length": TAMANHO_MAX}, timeout=15)
            resposta.raise_for_status()
            fato = resposta.json().get("fact", "").strip()
            if fato:
                return fato
        except (requests.RequestException, ValueError) as erro:
            print(f"⚠️ Tentativa {tentativa} falhou: {erro}")
            time.sleep(2)
    raise RuntimeError("Não foi possível obter uma mensagem da API.")


def buscar_mensagens(quantidade):
    mensagens = []
    repetidas = 0
    while len(mensagens) < quantidade:
        fato = buscar_mensagem()
        if fato in mensagens and repetidas < 10:   # evita repetir a mesma mensagem no vídeo
            repetidas += 1
            continue
        mensagens.append(fato)
        print(f"🐱 Mensagem {len(mensagens)}: {fato}")
    return mensagens


# ---------------------------------------------------------------- áudio

def gerar_audio(texto, caminho):
    gTTS(text=texto, lang=IDIOMA_VOZ).save(caminho)
    return caminho


# ---------------------------------------------------------------- imagem com texto

def fonte(tamanho):
    for caminho in FONTES:
        if os.path.exists(caminho):
            return ImageFont.truetype(caminho, tamanho)
    return ImageFont.load_default(tamanho)


def quebrar_linhas(texto, fnt, largura_max, draw):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if draw.textlength(teste, font=fnt) <= largura_max:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def desenhar_bloco(draw, linhas, fnt, y, cor, espaco=12, stroke=4):
    for linha in linhas:
        largura = draw.textlength(linha, font=fnt)
        draw.text(((LARGURA - largura) / 2, y), linha, font=fnt, fill=cor,
                  stroke_width=stroke, stroke_fill=(0, 0, 0))
        y += fnt.size + espaco
    return y


def montar_imagem(caminho_fundo, mensagem):
    """Abre o fundo, ajusta para 1280x720 e escreve a mensagem centralizada."""
    fundo = Image.open(caminho_fundo).convert("RGB")
    escala = max(LARGURA / fundo.width, ALTURA / fundo.height)
    fundo = fundo.resize((round(fundo.width * escala), round(fundo.height * escala)), Image.LANCZOS)
    x0, y0 = (fundo.width - LARGURA) // 2, (fundo.height - ALTURA) // 2
    img = fundo.crop((x0, y0, x0 + LARGURA, y0 + ALTURA)).convert("RGBA")

    medidor = ImageDraw.Draw(img)
    largura_max = LARGURA - 160
    espaco = 12
    # Diminui a fonte até o texto caber na tela
    for tamanho in range(68, 24, -4):
        fnt = fonte(tamanho)
        linhas = quebrar_linhas(mensagem, fnt, largura_max, medidor)
        altura = len(linhas) * (fnt.size + espaco) - espaco
        if altura <= ALTURA - 160:
            break

    # Painel semitransparente atrás do texto para dar leitura
    y = (ALTURA - altura) // 2
    painel = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(painel).rounded_rectangle((50, y - 40, LARGURA - 50, y + altura + 40),
                                             radius=30, fill=(0, 0, 0, 140))
    img = Image.alpha_composite(img, painel)

    desenhar_bloco(ImageDraw.Draw(img), linhas, fnt, y, (255, 255, 255), espaco)
    return img.convert("RGB")


# ---------------------------------------------------------------- vídeo

def listar_imagens():
    imagens = sorted(glob.glob(os.path.join(PASTA_IMGS, "*.jpg")) +
                     glob.glob(os.path.join(PASTA_IMGS, "*.jpeg")) +
                     glob.glob(os.path.join(PASTA_IMGS, "*.png")))
    if not imagens:
        sys.exit(f"Nenhuma imagem em {PASTA_IMGS}. Rode antes: python gerar_imagens.py")
    return imagens


def criar_video(quantidade, saida):
    os.makedirs(PASTA_TEMP, exist_ok=True)
    imagens = listar_imagens()
    mensagens = buscar_mensagens(quantidade)

    clipes, audios = [], []
    for i, mensagem in enumerate(mensagens, start=1):
        caminho_audio = os.path.join(PASTA_TEMP, f"audio_{i}.mp3")
        gerar_audio(mensagem, caminho_audio)
        audio = AudioFileClip(caminho_audio)
        audios.append(audio)

        fundo = random.choice(imagens)
        print(f"🖼️ Cena {i}: {os.path.basename(fundo)} ({audio.duration:.1f}s de áudio)")
        quadro = montar_imagem(fundo, mensagem)
        quadro.save(os.path.join(PASTA_TEMP, f"cena_{i}.jpg"), quality=90)

        clipe = (ImageClip(np.array(quadro))
                 .set_duration(audio.duration + PAUSA_FINAL)
                 .set_audio(audio)
                 .fadein(0.3).fadeout(0.3))
        clipes.append(clipe)

    video = concatenate_videoclips(clipes, method="compose")
    video.write_videofile(saida, fps=FPS, codec="libx264", audio_codec="aac",
                          threads=os.cpu_count(), preset="fast",
                          ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"])
    video.close()
    for audio in audios:
        audio.close()
    print(f"✅ Vídeo gerado: {saida}")


def main():
    parser = argparse.ArgumentParser(description="Gera um vídeo MP4 com curiosidades sobre gatos (catfact.ninja).")
    parser.add_argument("--quantidade", type=int, default=4, help="quantidade de mensagens / chamadas à API (padrão: 4)")
    parser.add_argument("--saida", help="caminho do .mp4 (padrão: output/video_gatos_<data>.mp4)")
    args = parser.parse_args()

    os.makedirs(PASTA_SAIDA, exist_ok=True)
    saida = args.saida or os.path.join(PASTA_SAIDA, f"video_gatos_{datetime.now():%Y%m%d_%H%M%S}.mp4")
    criar_video(args.quantidade, saida)


if __name__ == "__main__":
    main()
