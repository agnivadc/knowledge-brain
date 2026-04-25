from __future__ import annotations

import pytest

from knowledge_brain.token_utils import count_tokens


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", 0),
        ("   ", 0),
        ("\n\t  ", 0),
        ("hello", 1),
        ("hello world", 3),
        ("a b c d e f g h i j", 13),
    ],
)
def test_count_tokens_known_values(text: str, expected: int):
    assert count_tokens(text) == expected


def test_count_tokens_scales_with_word_count():
    assert count_tokens("a " * 100) == 130


def test_count_tokens_collapses_whitespace_runs():
    assert count_tokens("hello    world") == count_tokens("hello world")
