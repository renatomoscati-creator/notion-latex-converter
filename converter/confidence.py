EXOTIC_COMMANDS = {
    r"\llbracket", r"\rrbracket", r"\DeclareMathOperator",
    r"\operatorname", r"\mathscr", r"\mathfrak",
}

PLACEHOLDER_PATTERNS = [r"\square", r"\Box", "???"]


def has_unmatched_braces(latex: str) -> bool:
    return latex.count("{") != latex.count("}")


def score_latex_confidence(latex: str, low_confidence_flagged: bool) -> float:
    score = 1.0
    if low_confidence_flagged:
        score -= 0.4
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern in latex:
            score -= 0.2
    if has_unmatched_braces(latex):
        score -= 0.3
    for cmd in EXOTIC_COMMANDS:
        if cmd in latex:
            score -= 0.1
    return max(0.0, score)
