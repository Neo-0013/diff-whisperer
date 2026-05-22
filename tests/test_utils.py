import pytest
from utils import extract_json_from_text

def test_extract_pure_json():
    text = '{"story": "Once upon a code...", "risks": [], "improvements": []}'
    result = extract_json_from_text(text)
    assert result["story"] == "Once upon a code..."

def test_extract_json_with_markdown():
    text = """
    Here is the analysis:
    ```json
    {
        "story": "Markdown story",
        "risks": [{"category": "Security", "description": "None", "level": "Low"}],
        "improvements": ["More tests"]
    }
    ```
    I hope this helps!
    """
    result = extract_json_from_text(text)
    assert result["story"] == "Markdown story"
    assert len(result["risks"]) == 1

def test_extract_json_with_trailing_comma():
    # This tests the robust regex/cleaning capability
    text = '{"story": "Trailing comma", "risks": [],}'
    result = extract_json_from_text(text)
    assert result["story"] == "Trailing comma"

def test_extract_json_with_prefix_noise():
    text = 'ANALYSIS_START {"story": "Noise test"} ANALYSIS_END'
    result = extract_json_from_text(text)
    assert result["story"] == "Noise test"

def test_invalid_json():
    text = "This is not json at all."
    with pytest.raises(ValueError, match="Failed to extract valid JSON"):
        extract_json_from_text(text)

def test_extract_json_with_invalid_escape():
    # LLMs frequently output unescaped backslashes in regex or paths (like \s, \d, \p) which are invalid JSON escape sequences
    text = '{"story": "We modified regex \\s and path C:\\Users", "risks": [], "improvements": []}'
    result = extract_json_from_text(text)
    assert "\\s" in result["story"]
    assert "C:\\Users" in result["story"]


