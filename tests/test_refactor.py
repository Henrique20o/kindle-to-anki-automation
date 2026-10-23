import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import config
import main
from services import ai_service, anki_service, tts_service


def settings(**changes):
    values = dict(
        api_key="test-key",
        model="test-model",
        base_url="https://example.com/v1",
        difficulty="equilibrado",
        card_count=2,
        anki_deck="Inglês",
        anki_note_model="Omissão de Palavras",
        anki_url="http://localhost:8765",
        kindle_db_path="",
    )
    values.update(changes)
    return config.Settings(**values)


class ConfigTests(unittest.TestCase):
    def test_dotenv_is_loaded_and_environment_takes_precedence(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            fake_module = Path(tmp) / "config.py"
            (Path(tmp) / ".env").write_text("AI_API_KEY=file-key\nCARD_COUNT=3\n", encoding="utf-8")
            with patch.object(config, "__file__", str(fake_module)):
                with patch.dict(os.environ, {}, clear=True):
                    self.assertEqual(config.load_settings().api_key, "file-key")
                with patch.dict(os.environ, {"AI_API_KEY": "environment-key"}, clear=True):
                    self.assertEqual(config.load_settings().api_key, "environment-key")

    @patch("config.dotenv_values", return_value={})
    def test_custom_provider_requires_model_and_accepts_presets(self, _dotenv_values):
        with patch.dict(os.environ, {
            "AI_API_KEY": "custom-key",
            "AI_BASE_URL": "https://example.com/v1",
            "AI_MODEL": "custom-model",
            "CARD_DIFFICULTY": "avancado",
            "CARD_COUNT": "3",
        }, clear=True):
            result = config.load_settings()
        self.assertEqual((result.api_key, result.model, result.card_count), ("custom-key", "custom-model", 3))
        self.assertEqual(result.difficulty, "avancado")

        with patch.dict(os.environ, {
            "AI_API_KEY": "custom-key",
            "AI_BASE_URL": "https://example.com/v1",
        }, clear=True):
            with self.assertRaisesRegex(ValueError, "AI_MODEL"):
                config.load_settings()

    @patch("config.dotenv_values", return_value={})
    def test_missing_key_and_invalid_count_fail_early(self, _dotenv_values):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "AI_API_KEY"):
                config.load_settings()
        with patch.dict(os.environ, {"AI_API_KEY": "key", "CARD_COUNT": "4"}, clear=True):
            with self.assertRaisesRegex(ValueError, "CARD_COUNT"):
                config.load_settings()

    def test_save_preset_preserves_unrelated_lines(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            path = Path(tmp) / ".env"
            path.write_text("# minha chave\nAI_API_KEY=secret\nCARD_DIFFICULTY=facil\nANKI_DECK=English\n", encoding="utf-8")
            with patch.object(config, "__file__", str(Path(tmp) / "config.py")):
                with patch.dict(os.environ, {}, clear=True):
                    config.save_preset("CARD_DIFFICULTY", "avancado")
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                "# minha chave\nAI_API_KEY=secret\nCARD_DIFFICULTY=avancado\nANKI_DECK=English\n",
            )

    def test_save_preset_creates_env_and_respects_system_override(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            path = Path(tmp) / ".env"
            with patch.object(config, "__file__", str(Path(tmp) / "config.py")):
                with patch.dict(os.environ, {}, clear=True):
                    config.save_preset("CARD_COUNT", "1")
                self.assertEqual(path.read_text(encoding="utf-8"), "CARD_COUNT=1\n")
                with patch.dict(os.environ, {"CARD_COUNT": "3"}, clear=True):
                    with self.assertRaisesRegex(ValueError, "ambiente do sistema"):
                        config.save_preset("CARD_COUNT", "2")
                self.assertEqual(path.read_text(encoding="utf-8"), "CARD_COUNT=1\n")


class AiTests(unittest.TestCase):
    def test_prompt_uses_each_preset_and_count(self):
        for difficulty, levels in config.DIFFICULTY_PRESETS.items():
            for count in (1, 2, 3):
                with self.subTest(difficulty=difficulty, count=count):
                    prompt = ai_service.build_prompt("match(fósforo)", settings(difficulty=difficulty, card_count=count))
                    self.assertIn(f"exactly {count}", prompt)
                    self.assertIn(f"{levels[0]} and {levels[1]}", prompt)
                    self.assertIn("match(fósforo)", prompt)

    def test_invalid_response_is_rejected_before_sending(self):
        for content in ('not JSON', '{"sentences": []}', '{"sentences": [{"sentence": "Hello"}]}'):
            with self.subTest(content=content), self.assertRaises(ValueError):
                ai_service.parse_sentences(content, 2)

    @patch("services.ai_service.OpenAI")
    def test_client_uses_configured_provider(self, openai_class):
        openai_class.return_value.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=(
                '{"sentences": [{"sentence": "One", "translation": "Um"}, '
                '{"sentence": "Two", "translation": "Dois"}]}'
            )))]
        )
        result = ai_service.generate_sentences("word", settings())
        self.assertEqual(len(result), 2)
        openai_class.assert_called_once_with(api_key="test-key", base_url="https://example.com/v1")
        self.assertEqual(openai_class.return_value.chat.completions.create.call_args.kwargs["model"], "test-model")


class AnkiTests(unittest.TestCase):
    @patch("services.anki_service.requests.post")
    def test_success_and_error_response(self, post):
        post.return_value.json.return_value = {"result": 123, "error": None}
        result = anki_service.send_to_anki("{{c1::word}}", "palavra", r"C:\audio\one.mp3", settings())
        self.assertEqual(result, 123)
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["params"]["note"]["deckName"], "Inglês")
        self.assertEqual(payload["params"]["note"]["audio"][0]["filename"], "one.mp3")
        self.assertEqual(post.call_args.kwargs["timeout"], 30)

        post.return_value.json.return_value = {"result": None, "error": "deck not found"}
        with self.assertRaisesRegex(RuntimeError, "deck not found"):
            anki_service.send_to_anki("{{c1::word}}", "palavra", "one.mp3", settings())

        post.return_value.raise_for_status.side_effect = RuntimeError("HTTP error")
        with self.assertRaisesRegex(RuntimeError, "HTTP error"):
            anki_service.send_to_anki("{{c1::word}}", "palavra", "one.mp3", settings())


class FlowTests(unittest.TestCase):
    def test_invalid_spaced_meaning_is_not_processed(self):
        words, invalid = main.split_words_input("cat, match (fósforo); dog|walk")
        self.assertEqual(words, ["cat", "dog", "walk"])
        self.assertEqual(invalid, ["match (fósforo)"])

    @patch("main.add_word")
    @patch("main.has_word", return_value=False)
    @patch("main.generate_sentences")
    @patch("main.generate_audio")
    @patch("main.send_to_anki")
    def test_partial_send_does_not_register_word_and_cleans_audio(
        self, send, audio, sentences, _has_word, add_word
    ):
        sentences.return_value = [
            {"sentence": "One", "translation": "Um"},
            {"sentence": "Two", "translation": "Dois"},
        ]
        send.side_effect = [123, RuntimeError("Anki unavailable")]
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            paths = [Path(tmp) / "one.mp3", Path(tmp) / "two.mp3"]
            for path in paths:
                path.write_bytes(b"audio")
            audio.side_effect = [str(path) for path in paths]
            status = main.process_word("word", settings())
            self.assertEqual(status, "error")
            self.assertTrue(all(not path.exists() for path in paths))
        add_word.assert_not_called()

    @patch("main.process_word", side_effect=[RuntimeError("bad"), "ok"])
    def test_batch_continues_after_error(self, process):
        main.process_words_batch(["first", "second"], settings())
        self.assertEqual(process.call_count, 2)

    @patch("main.add_word")
    @patch("main.has_word", return_value=False)
    @patch("main.generate_sentences", return_value=[{"sentence": "One", "translation": "Um"}])
    @patch("main.generate_audio", return_value="one.mp3")
    @patch("main.send_to_anki", return_value=123)
    @patch("main.cleanup_audio")
    def test_complete_send_registers_word(self, _cleanup, _send, _audio, _sentences, _has_word, add_word):
        self.assertEqual(main.process_word("word", settings(card_count=1)), "ok")
        add_word.assert_called_once_with("word")

    @patch("main.load_settings", return_value=settings(kindle_db_path="C:/kindle/vocab.db"))
    @patch("main.extract_words_from_kindle_db", return_value=["word"])
    @patch("main.process_words_batch")
    @patch("builtins.input", side_effect=["kindle", "", "", "sair"])
    def test_kindle_uses_configured_path_when_enter_is_pressed(self, _input, batch, extract, _load):
        main.main()
        extract.assert_called_once_with("C:/kindle/vocab.db", limit=None)
        batch.assert_called_once_with(["word"], settings(kindle_db_path="C:/kindle/vocab.db"))


class MenuTests(unittest.TestCase):
    def test_menu_saves_both_presets_and_applies_them_immediately(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            path = Path(tmp) / ".env"
            with patch.object(config, "__file__", str(Path(tmp) / "config.py")):
                with patch.dict(os.environ, {}, clear=True):
                    with patch("builtins.input", side_effect=["1", "3", "2", "1", "3"]):
                        updated = main.configure_cards(settings())
                with patch.dict(os.environ, {"AI_API_KEY": "test-key"}, clear=True):
                    reloaded = config.load_settings()
            self.assertEqual((updated.difficulty, updated.card_count), ("avancado", 1))
            self.assertEqual((reloaded.difficulty, reloaded.card_count), ("avancado", 1))
            self.assertIn("CARD_DIFFICULTY=avancado", path.read_text(encoding="utf-8"))
            self.assertIn("CARD_COUNT=1", path.read_text(encoding="utf-8"))

    @patch("main.save_preset")
    def test_invalid_choice_and_cancel_leave_settings_unchanged(self, save):
        with patch("builtins.input", side_effect=["1", "9", "2", "", "3"]):
            self.assertEqual(main.configure_cards(settings()), settings())
        save.assert_not_called()

    @patch("main.save_preset", side_effect=OSError("sem permissão"))
    def test_write_error_leaves_session_unchanged(self, _save):
        with patch("builtins.input", side_effect=["2", "1", "3"]):
            self.assertEqual(main.configure_cards(settings()), settings())

    @patch("main.load_settings", return_value=settings())
    @patch("main.save_preset")
    @patch("main.process_word")
    @patch("builtins.input", side_effect=["config", "1", "3", "3", "word", "sair"])
    def test_next_word_receives_updated_settings(self, _input, process, _save, _load):
        main.main()
        self.assertEqual(process.call_args.args[1].difficulty, "avancado")


class AudioTests(unittest.TestCase):
    @patch("services.tts_service.gTTS")
    def test_partial_temporary_audio_is_removed_after_failure(self, gtts):
        def partial_save(path):
            Path(path).write_bytes(b"partial")
            raise RuntimeError("audio unavailable")

        gtts.return_value.save.side_effect = partial_save
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmp:
            fake_module = Path(tmp) / "services" / "tts_service.py"
            with patch.object(tts_service, "__file__", str(fake_module)):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.assertIsNone(tts_service.generate_audio("hello", retries=1))
            self.assertEqual(list((Path(tmp) / "audio").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
