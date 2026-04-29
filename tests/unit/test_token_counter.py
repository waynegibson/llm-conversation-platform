from services.token_counter import estimate_tokens, trim_history_by_token_budget


class _Msg:
    def __init__(self, content: str):
        self.content = content


def test_estimate_tokens_has_minimum_of_one() -> None:
    assert estimate_tokens("") == 1
    assert estimate_tokens("abc") == 1


def test_trim_history_keeps_newest_messages_within_budget() -> None:
    messages = [
        _Msg("old message"),
        _Msg("middle message with more text"),
        _Msg("latest"),
    ]

    trimmed = trim_history_by_token_budget(messages, token_budget=15)

    assert len(trimmed) >= 1
    assert trimmed[-1].content == "latest"
