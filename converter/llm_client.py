import os
from google import genai
from google.genai import types
from converter.normalizer import extract_confidence_sentinel, strip_markdown_fences
from converter.confidence import score_latex_confidence


class ConversionError(Exception):
    pass


def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Add it to your .env file. "
            "Get a free key at https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=api_key)


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


def _build_result(raw_text: str) -> dict:
    raw_text = strip_markdown_fences(raw_text)
    clean, is_low = extract_confidence_sentinel(raw_text)
    confidence = score_latex_confidence(clean, is_low)
    return {"latex": clean, "confidence": confidence, "raw_response": raw_text}


def convert_text_to_latex(client, user_input: str, output_mode: str) -> dict:
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    try:
        response = client.models.generate_content(
            model=model,
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=_build_system_prompt(output_mode),
                max_output_tokens=1024,
            ),
        )
        raw = response.text
    except Exception as e:
        raise ConversionError(f"API call failed: {e}") from e
    return _build_result(raw)


def convert_image_to_latex(client, image_b64: str, media_type: str, output_mode: str) -> dict:
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    try:
        import base64 as _base64
        image_part = types.Part(
            inline_data=types.Blob(
                mime_type=media_type,
                data=_base64.b64decode(image_b64),
            )
        )
        response = client.models.generate_content(
            model=model,
            contents=[image_part, "Extract the mathematical expression as LaTeX."],
            config=types.GenerateContentConfig(
                system_instruction=_build_system_prompt(output_mode),
                max_output_tokens=1024,
            ),
        )
        raw = response.text
    except Exception as e:
        raise ConversionError(f"API call failed: {e}") from e
    return _build_result(raw)
