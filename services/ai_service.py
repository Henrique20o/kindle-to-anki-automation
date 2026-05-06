from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_sentences(word):
    prompt = f"""
You are an English teacher.

Create 2 simple and natural sentences in English using the word: "{word}".

Rules:
- Preferably, sentence 1 should be level B1
- Preferably, sentence 2 should be level B2
- Use the word clearly in ALL sentences
- Keep them natural and useful
- Create the translation in Brazilian Portuguese
- If the word includes a meaning in parentheses (in Portuguese or English), use ONLY that meaning in all sentences.
- Do not use any other meaning of the word.

Example:
Input: "match (fósforo)"
→ sentences must refer to fire, not sports or pairing.

Return ONLY JSON in this format:

{{
  "sentences": [
    {{
      "sentence": "...",
      "translation": "..."
    }},
    {{
      "sentence": "...",
      "translation": "..."
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
        return data["sentences"]
    except Exception as e:
        print("Erro ao interpretar JSON:", e)
        print("Resposta da IA:", content)
        return []