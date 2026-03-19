from converter.confidence import score_latex_confidence, has_unmatched_braces

def test_clean_latex_high_score():
    score = score_latex_confidence(r"\frac{a}{b}", low_confidence_flagged=False)
    assert score >= 0.9

def test_model_flagged_low():
    score = score_latex_confidence(r"x^2", low_confidence_flagged=True)
    assert score <= 0.6

def test_unmatched_brace_penalty():
    score = score_latex_confidence(r"\frac{a}{b", low_confidence_flagged=False)
    assert score <= 0.7

def test_exotic_command_penalty():
    score = score_latex_confidence(r"\llbracket x \rrbracket", low_confidence_flagged=False)
    assert score < 0.9

def test_placeholder_penalty():
    score = score_latex_confidence(r"\square + x", low_confidence_flagged=False)
    assert score < 0.9

def test_has_unmatched_braces_true():
    assert has_unmatched_braces(r"\frac{a}{b") is True

def test_has_unmatched_braces_false():
    assert has_unmatched_braces(r"\frac{a}{b}") is False

def test_floor_at_zero():
    score = score_latex_confidence(
        r"\llbracket \square \Box ???", low_confidence_flagged=True
    )
    assert score >= 0.0
