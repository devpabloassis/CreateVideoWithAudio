# Create a Video with Audio in Python

A small, **educational** Python project that shows how to build an MP4 video from scratch by
combining **images**, **text overlays** and **narrated audio**.

The code is short on purpose, so it can be read from top to bottom in a few minutes. It is meant for
people learning Python who want to see, in one place, how to:

- call a REST API and read its JSON response (`requests`);
- turn text into speech and save it as MP3 (`gTTS`);
- open, resize and crop images, and draw text on them with a semi-transparent panel (`Pillow`);
- generate images from code, with gradients and blur effects (`Pillow`);
- join images and audio into video scenes and export an MP4 (`moviepy` + `ffmpeg`);
- organize a script with functions, constants and command-line arguments (`argparse`).

## What it does

The script creates a video with 4 cat facts from the [catfact.ninja](https://catfact.ninja/fact) API.
Each API call becomes one scene:

1. the fact is fetched from the API;
2. the text is converted into narrated audio (English voice);
3. a background image is picked at random from `imgs/`, and the text is drawn over it;
4. the scene lasts as long as its audio;
5. all the scenes are joined into `output/video_gatos_<date>.mp4`.

Example API response:

```json
{"fact": "A group of cats is called a “clowder.”", "length": 38}
```

## Installation (venv)

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

An internet connection is needed: the API provides the facts and gTTS generates the voice.

## Usage

```bash
python gerar_imagens.py           # creates imgs/fundo1.jpg, fundo2.jpg and fundo3.jpg (first time only)
python criar_video_gatos.py       # creates output/video_gatos_<date>.mp4
```

Options:

- `--quantidade N`: number of facts, which is also the number of API calls (default: 4)
- `--saida path.mp4`: output file

To use your own images (for example, cat photos), put `.jpg` or `.png` files in `imgs/`.
They are resized and cropped to 1280x720.

## Files

| File | Purpose |
|---|---|
| `criar_video_gatos.py` | Fetches the facts, generates the audio, builds the scenes and exports the MP4 |
| `gerar_imagens.py` | Creates 3 sample background images |
| `output/temp/` | Intermediate audio files (`audio_N.mp3`) and frames (`cena_N.jpg`) |

## Ideas to practice

- Change the voice language (`IDIOMA_VOZ`) or the video size (`LARGURA`, `ALTURA`).
- Use another API, for example jokes or quotes.
- Add background music, or a transition between scenes.
- Show the scene number or a title on each image.

The code comments and names are in Portuguese, the author's native language.
