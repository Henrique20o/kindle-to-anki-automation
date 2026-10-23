"""Envio de notas para o AnkiConnect."""

from pathlib import Path

import requests

from config import Settings


def send_to_anki(cloze_text: str, translation: str, audio_path: str, settings: Settings) -> int:
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": settings.anki_deck,
                "modelName": settings.anki_note_model,
                "fields": {
                    "Texto": cloze_text,
                    "Verso Extra": translation,
                },
                "audio": [{
                    "path": audio_path,
                    "filename": Path(audio_path).name,
                    "fields": ["Texto"],
                }],
            }
        },
    }

    response = requests.post(settings.anki_url, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Resposta inválida do AnkiConnect")
    if data.get("error"):
        raise RuntimeError(f"AnkiConnect: {data['error']}")
    note_id = data.get("result")
    if not isinstance(note_id, int) or isinstance(note_id, bool) or note_id <= 0:
        raise ValueError("AnkiConnect não confirmou a criação da nota")
    return note_id
