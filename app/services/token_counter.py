from models.entities import Message


def estimate_tokens(text: str) -> int:
    # Rough heuristic for local models when tokenizer-specific libraries are unavailable.
    return max(1, len(text) // 4)


def estimate_message_tokens(message: Message) -> int:
    return estimate_tokens(message.content) + 4


def trim_history_by_token_budget(messages: list[Message], token_budget: int) -> list[Message]:
    if token_budget <= 0:
        return messages

    total = 0
    selected: list[Message] = []
    for message in reversed(messages):
        needed = estimate_message_tokens(message)
        if total + needed > token_budget and selected:
            break
        selected.append(message)
        total += needed

    return list(reversed(selected))
