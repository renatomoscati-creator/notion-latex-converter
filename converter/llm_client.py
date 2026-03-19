import os
import anthropic
from converter.normalizer import extract_confidence_sentinel, strip_markdown_fences
from converter.confidence import score_latex_confidence


class ConversionError(Exception):
    pass


def get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return anthropic.Anthropic(api_key=api_key)


def _build_system_prompt(output_mode: str) -> str:
    wrap = "$$\n...\n$$" if output_mode == "block" else r"\(" + "\n...\n" + r"\)"
    return f"""You are a LaTeX transcription engine for Notion equation blocks.

RULES:
1. Respond with ONLY the LaTeX expression. No explanation. No markdown fences. No prose.
2. Use \\frac{{a}}{{b}} for fractions — never a/b.
3. Use ^ for exponents (x^2), _ for subscripts (x_1).
4. Use \\sqrt{{x}}, \\alpha, \\beta, \\gamma, \\sum_{{i=1}}^{{n}}, \\int_0^1.
5. Do NOT use \\begin{{align}}, \\begin{{equation}}, or any display environment.
6. Convert Unicode Greek letters to LaTeX commands (α → \\alpha, β → \\beta).
7. Do not use exotic packages or macros not supported in KaTeX/MathJax.
8. Output mode is {output_mode.upper()}. Wrap your result exactly as: {wrap}
9. If the input is ambiguous or image is unclear, prefix with: [LOW_CONFIDENCE]
"""


def _parse_response(response) -> str:
    raw = response.content[0].text
    return strip_markdown_fences(raw)


def _build_result(raw_text: str) -> dict:
    clean, is_low = extract_confidence_sentinel(raw_text)
    confidence = score_latex_confidence(clean, is_low)
    return {"latex": clean, "confidence": confidence, "raw_response": raw_text}


def convert_text_to_latex(client, user_input: str, output_mode: str) -> dict:
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=_build_system_prompt(output_mode),
            messages=[{"role": "user", "content": user_input}],
        )
    except anthropic.APIError as e:
        raise ConversionError(f"API call failed: {e}") from e
    raw = _parse_response(response)
    return _build_result(raw)


def convert_image_to_latex(client, image_b64: str, media_type: str, output_mode: str) -> dict:
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=_build_system_prompt(output_mode),
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": "Extract the mathematical expression as LaTeX."},
                ],
            }],
        )
    except anthropic.APIError as e:
        raise ConversionError(f"API call failed: {e}") from e
    raw = _parse_response(response)
    return _build_result(raw)
