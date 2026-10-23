"""Geração e validação de frases pela API de IA configurada."""

import json
import random

from openai import OpenAI

from config import DIFFICULTY_PRESETS, Settings


QUESTION_RATE = 0.45


def build_prompt(word: str, settings: Settings) -> str:
    levels = DIFFICULTY_PRESETS[settings.difficulty]
    question_rule = (
        "Make exactly 1 sentence a natural question"
        if random.random() < QUESTION_RATE
        else "Do not use questions; all sentences must be declarative"
    )

    return f"""You are an English teacher.

Create exactly {settings.card_count} simple and natural sentences in English using the word: "{word}".

Rules:
- Aim for CEFR levels {levels[0]} and {levels[1]}.
- Use the word clearly in ALL sentences.
- Keep them natural and useful.
- Write sentences using different tenses when possible (present, past, and future).
- Use different points of view when possible (first, second, and third person).
- Create varied contexts whenever possible.
- {question_rule}.
- Create the translation in Brazilian Portuguese for every sentence.
- If the word includes a meaning in parentheses (in Portuguese or English), use ONLY that meaning in all sentences.
- Do not use any other meaning of the word.

Example:
Input: "match(fósforo)"
→ sentences must refer to fire, not sports or pairing.

Return ONLY JSON in this format, with exactly {settings.card_count} items:
{{"sentences": [{{"sentence": "...", "translation": "..."}}]}}
"""


def parse_sentences(content: str, expected_count: int) -> list[dict[str, str]]:
    try:
        data = json.loads(content)
        sentences = data["sentences"]
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError("A IA não retornou JSON com a lista 'sentences'") from exc

    if not isinstance(sentences, list) or len(sentences) != expected_count:
        raise ValueError(f"A IA deve retornar exatamente {expected_count} frases")

    for item in sentences:
        if not isinstance(item, dict) or not all(
            isinstance(item.get(field), str) and item[field].strip()
            for field in ("sentence", "translation")
        ):
            raise ValueError("A IA retornou frase ou tradução vazia")

    return sentences


def generate_sentences(word: str, settings: Settings) -> list[dict[str, str]]:
    client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)
    response = client.chat.completions.create(
        model=settings.model,
        messages=[{"role": "user", "content": build_prompt(word, settings)}],
        temperature=0.5,
    )
    if not response.choices:
        raise ValueError("A IA não retornou opções de resposta")
    return parse_sentences(response.choices[0].message.content or "", settings.card_count)
