from __future__ import annotations

_TOKENS_PER_WORD = 1.3


def count_tokens(text: str) -> int:
    """Approximate token count via word-based heuristic (~1.3 tokens/word)."""
    return round(len(text.split()) * _TOKENS_PER_WORD)
