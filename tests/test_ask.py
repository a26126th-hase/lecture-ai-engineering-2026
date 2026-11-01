"""Tests for the ask command-line interface."""

import sys
from types import SimpleNamespace

from app import ask as ask_module


def test_chat_option_starts_chat_with_positional_question(monkeypatch, capsys):
    received = []
    monkeypatch.setattr(sys, "argv", ["app.ask", "--chat", "LoRAとは何ですか？"])
    monkeypatch.setattr(ask_module, "chat", received.append)
    monkeypatch.setattr(ask_module, "ask", lambda question: "single response")

    ask_module.main()

    assert received == ["LoRAとは何ですか？"]
    assert "single response" not in capsys.readouterr().out


def test_chat_stops_when_input_is_blank(monkeypatch, capsys):
    sent_questions = []
    session = SimpleNamespace(
        send_message=lambda question: (
            sent_questions.append(question)
            or SimpleNamespace(
                text=f"response to {question}",
                usage_metadata=SimpleNamespace(
                    prompt_token_count=1,
                    candidates_token_count=2,
                ),
            )
        )
    )
    client = SimpleNamespace(chats=SimpleNamespace(create=lambda model: session))
    monkeypatch.setattr(ask_module.genai, "Client", lambda **kwargs: client)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    inputs = iter(["次の質問", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))

    ask_module.chat("最初の質問")

    assert sent_questions == ["最初の質問", "次の質問"]
    assert "response to 次の質問" in capsys.readouterr().out
