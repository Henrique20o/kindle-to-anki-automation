import requests

def send_to_anki(cloze_text, translation, audio_path):
    filename = audio_path.split("/")[-1]

    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": "Inglês",
                "modelName": "Omissão de Palavras",
                "fields": {
                    "Texto": cloze_text,
                    "Verso Extra": translation
                },
                "audio": [{
                    "path": audio_path,
                    "filename": filename,
                    "fields": ["Texto"]
                }]
            }
        }
    }

    response = requests.post("http://localhost:8765", json=payload)
    print(response.json())