# tests/test_normalizer.py
import pytest
from converter.normalizer import (
    normalize_fractions,
    normalize_greek,
    strip_unsupported_environments,
    normalize_display_delimiters,
    extract_confidence_sentinel,
    strip_markdown_fences,
    sanitize_for_katex,
    normalize,
)

def test_fraction_simple():
    assert normalize_fractions("a/b") == r"\frac{a}{b}"

def test_fraction_already_frac():
    assert normalize_fractions(r"\frac{a}{b}") == r"\frac{a}{b}"

def test_fraction_idempotent():
    result = normalize_fractions(r"\frac{a}{b}")
    assert normalize_fractions(result) == result

def test_greek_alpha():
    assert normalize_greek("α + β") == r"\alpha + \beta"

def test_greek_uppercase():
    assert normalize_greek("Γ") == r"\Gamma"

def test_strip_align_env():
    assert strip_unsupported_environments(r"\begin{align}x=1\end{align}") == "x=1"

def test_strip_equation_env():
    assert strip_unsupported_environments(r"\begin{equation}E=mc^2\end{equation}") == "E=mc^2"

def test_delimiter_block():
    assert normalize_display_delimiters("x^2", "block") == "$$\nx^2\n$$"

def test_delimiter_inline():
    assert normalize_display_delimiters("x^2", "inline") == r"\(" + "\nx^2\n" + r"\)"

def test_delimiter_rewrap_block_to_inline():
    latex = "$$\nx^2\n$$"
    result = normalize_display_delimiters(latex, "inline")
    assert result == r"\(" + "\nx^2\n" + r"\)"

def test_confidence_sentinel_present():
    clean, low = extract_confidence_sentinel("[LOW_CONFIDENCE]x^2")
    assert clean == "x^2"
    assert low is True

def test_confidence_sentinel_absent():
    clean, low = extract_confidence_sentinel("x^2")
    assert clean == "x^2"
    assert low is False

def test_strip_markdown_fences():
    assert strip_markdown_fences("```latex\nx^2\n```") == "x^2"
    assert strip_markdown_fences("```\nx^2\n```") == "x^2"

# ── KaTeX sanitization ────────────────────────────────────────────────────────

def test_boldsymbol_replaced_with_mathbf():
    assert sanitize_for_katex(r"\boldsymbol{x}") == r"\mathbf{x}"

def test_cancel_stripped():
    result = sanitize_for_katex(r"\cancel{x} + y")
    assert r"\cancel" not in result
    assert "x" in result

def test_xcancel_stripped():
    result = sanitize_for_katex(r"\xcancel{x}")
    assert r"\xcancel" not in result
    assert "x" in result

def test_bcancel_stripped():
    result = sanitize_for_katex(r"\bcancel{x}")
    assert r"\bcancel" not in result
    assert "x" in result

def test_operatorname_stripped():
    result = sanitize_for_katex(r"\operatorname{sgn}(x)")
    assert r"\operatorname" not in result

def test_DeclareMathOperator_stripped():
    result = sanitize_for_katex(r"\DeclareMathOperator{\sgn}{sgn}")
    assert r"\DeclareMathOperator" not in result

def test_hspace_stripped():
    result = sanitize_for_katex(r"x \hspace{1cm} y")
    assert r"\hspace" not in result

def test_vspace_stripped():
    result = sanitize_for_katex(r"x \vspace{1cm} y")
    assert r"\vspace" not in result

def test_tag_stripped():
    result = sanitize_for_katex(r"x = 1 \tag{1}")
    assert r"\tag" not in result

def test_label_stripped():
    result = sanitize_for_katex(r"x = 1 \label{eq:main}")
    assert r"\label" not in result

def test_ref_stripped():
    result = sanitize_for_katex(r"see \ref{eq:main}")
    assert r"\ref" not in result

def test_eqref_stripped():
    result = sanitize_for_katex(r"see \eqref{eq:main}")
    assert r"\eqref" not in result

def test_safe_commands_untouched():
    expr = r"\frac{a}{b} + \sqrt{x} + \alpha"
    assert sanitize_for_katex(expr) == expr

def test_normalize_pipeline():
    result = normalize("α/β", output_mode="block")
    assert r"\alpha" in result
    assert r"\beta" in result
    assert r"\frac" in result
