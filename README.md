# Vídeo de Curiosidades sobre Gatos com Python

Gera um vídeo MP4 com 4 curiosidades sobre gatos da API [catfact.ninja](https://catfact.ninja/fact).
Cada chamada à API vira uma cena: uma imagem de fundo escolhida ao acaso entre as 3 de `imgs/`, o texto
da mensagem escrito sobre ela e a narração em áudio. Cada cena dura o tempo do seu áudio.

Exemplo de resposta da API:

```json
{"fact": "A group of cats is called a “clowder.”", "length": 38}
```

## Instalação (venv)

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Precisa de internet: a API fornece as mensagens e o gTTS gera a voz.

## Uso

```bash
python gerar_imagens.py           # cria imgs/fundo1.jpg, fundo2.jpg e fundo3.jpg (só na 1ª vez)
python criar_video_gatos.py       # gera output/video_gatos_<data>.mp4
```

Opções:

- `--quantidade N`: quantidade de mensagens/chamadas à API (padrão: 4)
- `--saida caminho.mp4`: arquivo de saída

Para usar suas próprias imagens (por exemplo, fotos de gatos), coloque arquivos `.jpg`/`.png` em `imgs/`.
Elas são ajustadas para 1280x720.

## Arquivos

| Arquivo | Função |
|---|---|
| `criar_video_gatos.py` | Busca as mensagens, gera os áudios, monta as cenas e exporta o MP4 |
| `gerar_imagens.py` | Cria 3 imagens de fundo de exemplo |
| `output/temp/` | Áudios (`audio_N.mp3`) e quadros (`cena_N.jpg`) intermediários |
