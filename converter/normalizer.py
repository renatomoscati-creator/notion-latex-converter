# converter/normalizer.py
import re

GREEK_MAP = {
    "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta",
    "ε": r"\epsilon", "ζ": r"\zeta", "η": r"\eta", "θ": r"\theta",
    "ι": r"\iota", "κ": r"\kappa", "λ": r"\lambda", "μ": r"\mu",
    "ν": r"\nu", "ξ": r"\xi", "π": r"\pi", "ρ": r"\rho",
    "σ": r"\sigma", "τ": r"\tau", "υ": r"\upsilon", "φ": r"\phi",
    "χ": r"\chi", "ψ": r"\psi", "ω": r"\omega",
    "Γ": r"\Gamma", "Δ": r"\Delta", "Θ": r"\Theta", "Λ": r"\Lambda",
    "Ξ": r"\Xi", "Π": r"\Pi", "Σ": r"\Sigma", "Υ": r"\Upsilon",
    "Φ": r"\Phi", "Ψ": r"\Psi", "Ω": r"\Omega",
}

UNSUPPORTED_ENVS = ["align", "align*", "equation", "equation*", "array", "eqnarray"]


def strip_markdown_fences(latex: str) -> str:
    latex = latex.strip()
    latex = re.sub(r"^```(?:latex)?\n?", "", latex)
    latex = re.sub(r"\n?```$", "", latex)
    return latex.strip()


def normalize_fractions(latex: str) -> str:
    pattern = r"(?<!\\)(?<!\{)([A-Za-z0-9\u0080-\uFFFF]+)\s*/\s*([A-Za-z0-9\u0080-\uFFFF]+)(?!\})"
    replacement = r"\\frac{\1}{\2}"
    return re.sub(pattern, replacement, latex)


def normalize_greek(latex: str) -> str:
    for char, cmd in GREEK_MAP.items():
        latex = latex.replace(char, cmd)
    return latex


def strip_unsupported_environments(latex: str) -> str:
    for env in UNSUPPORTED_ENVS:
        pattern = rf"\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}"
        latex = re.sub(pattern, r"\1", latex, flags=re.DOTALL)
    return latex.strip()


def _strip_existing_delimiters(latex: str) -> str:
    latex = latex.strip()
    if latex.startswith("$$") and latex.endswith("$$"):
        latex = latex[2:-2].strip()
    elif latex.startswith(r"\(") and latex.endswith(r"\)"):
        latex = latex[2:-2].strip()
    return latex.strip()


def normalize_display_delimiters(latex: str, output_mode: str) -> str:
    inner = _strip_existing_delimiters(latex)
    if output_mode == "block":
        return f"$$\n{inner}\n$$"
    else:
        return f"\\(\n{inner}\n\\)"


def extract_confidence_sentinel(latex: str) -> tuple[str, bool]:
    latex = latex.strip()
    if latex.startswith("[LOW_CONFIDENCE]"):
        return latex[len("[LOW_CONFIDENCE]"):].strip(), True
    return latex, False


def normalize(latex: str, output_mode: str = "block") -> str:
    latex = strip_markdown_fences(latex)
    latex, _ = extract_confidence_sentinel(latex)
    latex = strip_unsupported_environments(latex)
    latex = normalize_fractions(latex)
    latex = normalize_greek(latex)
    latex = normalize_display_delimiters(latex, output_mode)
    return latex
