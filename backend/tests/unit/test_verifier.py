# unit tests for verifier numeric extraction
import re
import pytest


def extractNumbers(text: str) -> list[str]:
    return re.findall(r"\b\d[\d,\.]*\b", text)


def test_extractNumbers_basic():
    result = extractNumbers("The movie had 1,234 viewers and 89.5% completion.")
    assert "1,234" in result
    assert "89.5" in result


def test_extractNumbers_empty():
    assert extractNumbers("No numbers here.") == []


def test_extractNumbers_large():
    result = extractNumbers("Revenue was $2,100,000 last quarter.")
    assert "2,100,000" in result
