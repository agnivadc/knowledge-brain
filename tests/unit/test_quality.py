from __future__ import annotations

import pytest

from knowledge_brain.models import InputValidationError
from knowledge_brain.quality import validate_query_input, validate_write_input


class TestValidateWriteInput:
    def test_happy_path_returns_none(self):
        assert validate_write_input("hello", ["t"], 100) is None

    def test_empty_content_rejected(self):
        with pytest.raises(InputValidationError, match="content must not be empty"):
            validate_write_input("", ["t"], 100)

    def test_whitespace_only_content_rejected(self):
        with pytest.raises(InputValidationError, match="content must not be empty"):
            validate_write_input("   \n\t  ", ["t"], 100)

    def test_empty_tags_rejected(self):
        with pytest.raises(InputValidationError, match="at least one tag"):
            validate_write_input("hello", [], 100)

    def test_oversize_content_rejected_with_token_count(self):
        long = " ".join(["word"] * 200)  # ~260 tokens
        with pytest.raises(InputValidationError) as exc_info:
            validate_write_input(long, ["t"], max_input_tokens=100)
        msg = str(exc_info.value)
        assert "260" in msg
        assert "100" in msg

    def test_at_token_limit_accepted(self):
        text = " ".join(["w"] * 76)  # 76*1.3 = 98.8 → 99 tokens
        validate_write_input(text, ["t"], max_input_tokens=99)


class TestValidateQueryInput:
    def test_happy_path_returns_none(self):
        assert validate_query_input("search", 100) is None

    def test_empty_query_rejected(self):
        with pytest.raises(InputValidationError, match="query must not be empty"):
            validate_query_input("", 100)

    def test_whitespace_only_query_rejected(self):
        with pytest.raises(InputValidationError, match="query must not be empty"):
            validate_query_input("   ", 100)

    def test_oversize_query_rejected_with_token_count(self):
        long = " ".join(["q"] * 200)
        with pytest.raises(InputValidationError) as exc_info:
            validate_query_input(long, max_input_tokens=10)
        msg = str(exc_info.value)
        assert "10" in msg
