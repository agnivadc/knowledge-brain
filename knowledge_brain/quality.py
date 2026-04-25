from __future__ import annotations

from .models import InputValidationError
from .token_utils import count_tokens


def validate_write_input(content: str, tags: list[str], max_input_tokens: int) -> None:
    if not content.strip():
        raise InputValidationError("content must not be empty")
    if not tags:
        raise InputValidationError("at least one tag is required")
    n = count_tokens(content)
    if n > max_input_tokens:
        raise InputValidationError(
            f"content has {n} tokens, exceeds max_input_tokens={max_input_tokens}"
        )


def validate_query_input(query: str, max_input_tokens: int) -> None:
    if not query.strip():
        raise InputValidationError("query must not be empty")
    n = count_tokens(query)
    if n > max_input_tokens:
        raise InputValidationError(
            f"query has {n} tokens, exceeds max_input_tokens={max_input_tokens}"
        )
