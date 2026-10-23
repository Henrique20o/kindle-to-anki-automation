from gtts import gTTS
import uuid
import os
import time
import traceback


def _sanitize_text(text):
    if text is None:
        return ""
    # Remove control characters and normalize whitespace
    cleaned = "".join(ch for ch in text if ord(ch) >= 32 or ch == "\n")
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()


def generate_audio(sentence, retries=3, backoff=1.0):
    """
    Generate an mp3 file for `sentence` using gTTS.
    On failure, retries a few times with exponential backoff and logs the full traceback
    and the failing sentence to the console for debugging.
    Returns the path to the mp3 file or None on failure.
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    AUDIO_DIR = os.path.join(BASE_DIR, "audio")

    os.makedirs(AUDIO_DIR, exist_ok=True)

    cleaned = _sanitize_text(sentence)

    if not cleaned:
        print("Aviso: frase vazia para gerar áudio")
        return None

    filename = f"{uuid.uuid4()}.mp3"
    path = os.path.join(AUDIO_DIR, filename)
    tmp_path = path + ".tmp"

    attempt = 0
    while attempt < retries:
        try:
            tts = gTTS(cleaned, lang='en')
            # Save to a temp path first to avoid partial files on failure
            tts.save(tmp_path)
            os.replace(tmp_path, path)
            return path
        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            attempt += 1
            print(f"Erro ao gerar áudio (tentativa {attempt}/{retries}):", e)
            print("Frase:", repr(cleaned))
            traceback.print_exc()
            if attempt >= retries:
                print("Falha ao gerar áudio após varias tentativas. Pulando frase.")
                return None
            # exponential backoff
            time.sleep(backoff * (2 ** (attempt - 1)))
