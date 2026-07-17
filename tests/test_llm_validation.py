import pytest
from unittest.mock import patch
from app.services.llm import generate_test_cases, LLMGenerationError

VALID_JSON = '''[
  {"title": "T1", "steps": ["a", "b"], "expected_result": "x"},
  {"title": "T2", "steps": ["a"], "expected_result": "y"},
  {"title": "T3", "steps": ["a"], "expected_result": "z"}
]'''

MALFORMED_JSON = "Sure, here are some test cases: not valid json at all"


def test_valid_response_is_parsed():
    with patch("app.services.llm._call_groq", return_value=VALID_JSON):
        result = generate_test_cases("some requirement text")
        assert len(result) == 3


def test_malformed_response_raises_after_retries():
    with patch("app.services.llm._call_groq", return_value=MALFORMED_JSON):
        with pytest.raises(LLMGenerationError):
            generate_test_cases("some requirement text", max_retries=1)