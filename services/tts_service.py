from gtts import gTTS
import uuid
import os

def generate_audio(sentence):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    AUDIO_DIR = os.path.join(BASE_DIR, "audio")

    os.makedirs(AUDIO_DIR, exist_ok=True)

    filename = f"{uuid.uuid4()}.mp3"
    path = os.path.join(AUDIO_DIR, filename)

    try:
        tts = gTTS(sentence, lang='en')
        tts.save(path)
    except Exception as e:
        print("Erro ao gerar áudio:", e)
        return None

    return path