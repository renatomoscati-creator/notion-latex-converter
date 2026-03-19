import pytest
from converter.llm_client import convert_text_to_latex, convert_image_to_latex, ConversionError


def test_text_calls_api_once(mock_anthropic_client):
    result = convert_text_to_latex(mock_anthropic_client, "x squared", "block")
    assert mock_anthropic_client.messages.create.call_count == 1


def test_text_returns_latex_key(mock_anthropic_client):
    result = convert_text_to_latex(mock_anthropic_client, "x squared", "block")
    assert "latex" in result
    assert isinstance(result["latex"], str)


def test_text_returns_confidence_key(mock_anthropic_client):
    result = convert_text_to_latex(mock_anthropic_client, "x squared", "block")
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0


def test_text_returns_raw_response_key(mock_anthropic_client):
    result = convert_text_to_latex(mock_anthropic_client, "x squared", "block")
    assert "raw_response" in result


def test_system_prompt_contains_block_mode(mock_anthropic_client):
    convert_text_to_latex(mock_anthropic_client, "x squared", "block")
    call_kwargs = mock_anthropic_client.messages.create.call_args
    system_prompt = call_kwargs.kwargs.get("system", "") or call_kwargs[1].get("system", "")
    assert "block" in system_prompt.lower() or "$$" in system_prompt


def test_system_prompt_contains_frac(mock_anthropic_client):
    convert_text_to_latex(mock_anthropic_client, "x squared", "block")
    call_kwargs = mock_anthropic_client.messages.create.call_args
    system_prompt = call_kwargs.kwargs.get("system", "") or call_kwargs[1].get("system", "")
    assert r"\frac" in system_prompt


def test_low_confidence_flagged(mock_anthropic_client_low_confidence):
    result = convert_text_to_latex(mock_anthropic_client_low_confidence, "blurry", "block")
    assert result["confidence"] <= 0.6


def test_api_error_raises_conversion_error(mock_anthropic_client_api_error):
    with pytest.raises(ConversionError):
        convert_text_to_latex(mock_anthropic_client_api_error, "x squared", "block")


def test_image_calls_api_once(mock_anthropic_client):
    result = convert_image_to_latex(mock_anthropic_client, "abc123", "image/png", "block")
    assert mock_anthropic_client.messages.create.call_count == 1


def test_image_returns_dict_shape(mock_anthropic_client):
    result = convert_image_to_latex(mock_anthropic_client, "abc123", "image/png", "inline")
    assert {"latex", "confidence", "raw_response"} <= result.keys()
