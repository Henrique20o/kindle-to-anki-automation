import json
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parent.parent / "words.json"


def load_words():
    if not FILE_PATH.exists():
        return {"words": []}

    try:
        content = FILE_PATH.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception:
        return {"words": []}


def save_words(data):
    FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = FILE_PATH.with_name(FILE_PATH.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
    tmp.replace(FILE_PATH)


def has_word(word: str) -> bool:
    data = load_words()
    target = (word or "").strip().lower()
    return any((w or "").strip().lower() == target for w in data.get("words", []))


def add_word(word: str) -> bool:
    if not word or not word.strip():
        return False

    data = load_words()
    normalized = (word or "").strip()

    if has_word(normalized):
        return False

    data.setdefault("words", []).append(normalized)
    save_words(data)
    return True

