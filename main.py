from services.tts_service import generate_audio
from services.anki_service import send_to_anki
from services.ai_service import generate_sentences
from services.word_service import has_word, add_word
from services.kindle_service import extract_words_from_kindle_db
import os


def cleanup_audio(paths):
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print("Erro ao deletar áudio:", e)


def process_word(word):
    word = (word or "").strip()
    if not word:
        return "invalid"

    if has_word(word):
        print(f"⚠️ Palavra '{word}' ja foi processada anteriormente\n")
        return "duplicate"

    print(f"\nGerando frases para: {word}...\n")
    sentences_data = generate_sentences(word)

    if not sentences_data:
        print("❌ Erro ao gerar frases\n")
        return "error"

    audio_paths = []
    sent_cards = 0

    for item in sentences_data:
        sentence = item.get("sentence", "").strip()
        translation = item.get("translation", "").strip()

        if not sentence:
            continue

        print(f"🟢 {sentence}")

        audio_path = generate_audio(sentence)
        if not audio_path:
            continue

        audio_paths.append(audio_path)
        cloze = f"{{{{c1::{sentence}}}}}"
        send_to_anki(cloze, translation, audio_path)
        sent_cards += 1

    cleanup_audio(audio_paths)

    if sent_cards == 0:
        print(f"❌ Nenhum card foi criado para '{word}'\n")
        return "error"

    add_word(word)
    print(f"\n✅ Finalizado para '{word}'\n")
    return "ok"


def process_words_batch(words):
    total = len(words)
    results = {"ok": 0, "duplicate": 0, "error": 0, "invalid": 0}

    for index, word in enumerate(words, start=1):
        print(f"\n[{index}/{total}] Palavra: {word}")
        status = process_word(word)
        results[status] = results.get(status, 0) + 1

    print("\n=== Resumo da importacao Kindle ===")
    print(f"Total: {total}")
    print(f"Processadas: {results['ok']}")
    print(f"Duplicadas: {results['duplicate']}")
    print(f"Invalidas: {results['invalid']}")
    print(f"Com erro: {results['error']}\n")


def main():

    print("=== Anki Automation ===")
    print("Digite uma palavra (ou 'sair' para encerrar)")
    print("Comando extra: 'kindle' para importar de um banco SQLite\n")

    while True:
        word = input("Palavra: ").strip()

        if word.lower() in ["sair", "exit", "quit"]:
            print("Encerrando...")
            break

        if word.lower() == "kindle":
            db_path = input("Caminho do arquivo .db do Kindle: ").strip().strip('"')

            if not db_path:
                print("⚠️ Caminho invalido\n")
                continue

            limit_text = input("Limite de palavras (Enter para todas): ").strip()
            limit = None
            if limit_text:
                if not limit_text.isdigit() or int(limit_text) <= 0:
                    print("⚠️ Limite invalido\n")
                    continue
                limit = int(limit_text)

            try:
                kindle_words = extract_words_from_kindle_db(db_path, limit=limit)
            except Exception as e:
                print("❌ Erro ao ler banco do Kindle:", e)
                continue

            if not kindle_words:
                print("⚠️ Nenhuma palavra encontrada no banco informado\n")
                continue

            print(f"\nEncontradas {len(kindle_words)} palavras no Kindle.")
            process_words_batch(kindle_words)
            continue

        if not word:
            print("⚠️ Digite uma palavra valida\n")
            continue

        process_word(word)


if __name__ == "__main__":
    main()