"""Configuração da aplicação, carregada uma vez no início da execução."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values, set_key


DIFFICULTY_PRESETS = {
    "facil": ("A2", "B1"),
    "equilibrado": ("B1", "B2"),
    "avancado": ("B2", "C1"),
}


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    base_url: str | None
    difficulty: str
    card_count: int
    anki_deck: str
    anki_note_model: str
    anki_url: str
    kindle_db_path: str


def _env_path() -> Path:
    return Path(__file__).resolve().parent / ".env"


def load_settings() -> Settings:
    file_values = dotenv_values(_env_path())

    def value(name: str, default: str = "") -> str:
        if name in os.environ:
            return os.environ[name]
        return file_values.get(name) or default

    api_key = (value("AI_API_KEY") or value("OPENAI_API_KEY")).strip()
    if not api_key:
        raise ValueError("Configure AI_API_KEY (ou OPENAI_API_KEY) no ambiente ou no .env")

    base_url = value("AI_BASE_URL").strip() or None
    if base_url and not base_url.startswith(("https://", "http://")):
        raise ValueError("AI_BASE_URL deve começar com https:// ou http://")

    model = value("AI_MODEL").strip()
    if base_url and not model:
        raise ValueError("Configure AI_MODEL ao usar AI_BASE_URL")
    model = model or "gpt-4o-mini"

    difficulty = value("CARD_DIFFICULTY", "equilibrado").strip().lower()
    if difficulty not in DIFFICULTY_PRESETS:
        raise ValueError("CARD_DIFFICULTY deve ser facil, equilibrado ou avancado")

    try:
        card_count = int(value("CARD_COUNT", "2"))
    except ValueError as exc:
        raise ValueError("CARD_COUNT deve ser 1, 2 ou 3") from exc
    if card_count not in (1, 2, 3):
        raise ValueError("CARD_COUNT deve ser 1, 2 ou 3")

    anki_deck = value("ANKI_DECK", "Inglês").strip()
    note_model = value("ANKI_NOTE_MODEL", "Omissão de Palavras").strip()
    anki_url = value("ANKI_URL", "http://localhost:8765").strip()
    if not anki_url.startswith(("https://", "http://")):
        raise ValueError("ANKI_URL deve começar com https:// ou http://")

    return Settings(
        api_key=api_key,
        model=model,
        base_url=base_url,
        difficulty=difficulty,
        card_count=card_count,
        anki_deck=anki_deck,
        anki_note_model=note_model,
        anki_url=anki_url,
        kindle_db_path=value("KINDLE_DB_PATH").strip(),
    )


def save_preset(name: str, value: str) -> None:
    """Salva um preset no .env sem alterar outras configurações."""
    allowed = {
        "CARD_DIFFICULTY": DIFFICULTY_PRESETS,
        "CARD_COUNT": ("1", "2", "3"),
    }
    if name not in allowed or value not in allowed[name]:
        raise ValueError("Preset inválido")
    if name in os.environ:
        raise ValueError(
            f"{name} está definido no ambiente do sistema. Remova essa variável para alterar pelo menu."
        )
    success, _, _ = set_key(_env_path(), name, value, quote_mode="never")
    if not success:
        raise OSError("Não foi possível salvar o .env")
