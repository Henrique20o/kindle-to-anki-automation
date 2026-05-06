import re
import sqlite3
from pathlib import Path

PREFERRED_WORD_COLUMNS = ("word", "stem", "lemma", "lookup", "token")
LANG_COLUMNS = ("lang", "language", "lang_code")


def normalize_word(value: str) -> str:
    text = (value or "").strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^[\W_]+|[\W_]+$", "", text)
    return text


def _is_valid_candidate(word: str) -> bool:
    if not word or len(word) < 2:
        return False
    if any(char.isdigit() for char in word):
        return False
    return True


def _list_tables(cursor: sqlite3.Cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]


def _list_columns(cursor: sqlite3.Cursor, table: str):
    cursor.execute(f'PRAGMA table_info("{table}")')
    return [row[1] for row in cursor.fetchall()]


def extract_words_from_kindle_db(db_path: str, language: str = "en", limit: int | None = None) -> list[str]:
    path = Path(db_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {path}")

    collected: list[str] = []
    seen: set[str] = set()

    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        cursor = conn.cursor()
        tables = _list_tables(cursor)

        for table in tables:
            columns = _list_columns(cursor, table)
            lower_map = {col.lower(): col for col in columns}

            word_col = next((lower_map[name] for name in PREFERRED_WORD_COLUMNS if name in lower_map), None)
            if not word_col:
                continue

            lang_col = next((lower_map[name] for name in LANG_COLUMNS if name in lower_map), None)

            query = f'SELECT DISTINCT "{word_col}" FROM "{table}" WHERE "{word_col}" IS NOT NULL AND TRIM("{word_col}") != ""'

            params: list[str] = []
            if lang_col and language:
                query += f' AND LOWER("{lang_col}") LIKE ?'
                params.append(f"{language.lower()}%")

            cursor.execute(query, params)
            for row in cursor.fetchall():
                candidate = normalize_word(str(row[0]))
                if not _is_valid_candidate(candidate):
                    continue

                key = candidate.lower()
                if key in seen:
                    continue

                seen.add(key)
                collected.append(candidate)

                if limit and len(collected) >= limit:
                    return collected

        return collected
    finally:
        conn.close()

