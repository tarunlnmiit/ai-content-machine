"""STM output normalization — strips Claude's filler from generated text.

Adapted from G0DM0D3 framework (elder-plinius).
Three passes: hedge removal → preamble stripping → casualization.

Usage:
    from lib.text_normalizer import normalize
    clean = normalize(claude_output)
"""

import re

# ── Hedge removal ─────────────────────────────────────────────────────────────

HEDGE_PATTERNS = [
    (r"\bI think\b,?\s*", ""),
    (r"\bI believe\b,?\s*", ""),
    (r"\bI feel\b,?\s*", ""),
    (r"\bperhaps\b,?\s*", ""),
    (r"\bmaybe\b,?\s*", ""),
    (r"\bsomewhat\b\s*", ""),
    (r"\bseems? to\b\s*", ""),
    (r"\bappears? to\b\s*", ""),
    (r"\bit seems\b,?\s*", ""),
    (r"\bit appears\b,?\s*", ""),
    (r"\bkind of\b\s*", ""),
    (r"\bsort of\b\s*", ""),
]

# ── Preamble stripping (sentence-initial) ─────────────────────────────────────

PREAMBLE_PATTERNS = [
    r"^Sure[!,.]?\s*",
    r"^Certainly[!,.]?\s*",
    r"^Of course[!,.]?\s*",
    r"^Absolutely[!,.]?\s*",
    r"^Great[!,.]?\s*",
    r"^Happy to help[!,.]?\s*",
    r"^I'd be happy to[^.]+\.\s*",
    r"^I'll help you[^.]+\.\s*",
    r"^Here(?:'s| is) (?:a |the )?(?:complete |full )?(?:carousel|post|script|blog|thread|caption)[^.]*\.\s*",
    r"^Here(?:'s| is) what I(?:'ve)? (?:created|generated|written|put together)[^.]*\.\s*",
]

# ── Casualization substitutions ───────────────────────────────────────────────

CASUAL_SUBS = [
    (r"\bHowever\b", "But"),
    (r"\bNevertheless\b", "Still"),
    (r"\bFurthermore\b", "Also"),
    (r"\bMoreover\b", "Plus"),
    (r"\bUtilize[sd]?\b", "Use"),
    (r"\bUtiliz(?:ing|ation)\b", "Using"),
    (r"\bImplement\b", "Build"),
    (r"\bLeverage[sd]?\b", "Use"),
    (r"\bGame.changer\b", "shift"),
    (r"\bSynergy\b", "teamwork"),
    (r"\bDive into\b", "Explore"),
    (r"\bDelve into\b", "Look at"),
]

# ── Banned words (content-machine specific) ───────────────────────────────────

BANNED = [
    (r"\bIn conclusion[,.]?\s*", ""),
    (r"\bIn summary[,.]?\s*", ""),
    (r"\bTo summarize[,.]?\s*", ""),
    (r"\bDive into\b\s*", "Explore "),
    (r"\bLeverage\b", "Use"),
    (r"\bGame.changer\b", "shift"),
    (r"\bSynergy\b", "teamwork"),
]


def _apply_patterns(text: str, patterns: list, flags: int = re.IGNORECASE) -> str:
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=flags)
    return text


def _strip_preambles(text: str) -> str:
    for pattern in PREAMBLE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
    return text


def _remove_banned(text: str) -> str:
    for pattern, replacement in BANNED:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    # Remove leading comma/space artifacts left after substitutions
    text = re.sub(r"^[,\s]+", "", text, flags=re.MULTILINE)
    return text


def _capitalize_sentences(text: str) -> str:
    """Re-capitalize sentence starts after stripping preambles."""
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.lstrip()
        if stripped and stripped[0].islower():
            line = line[:len(line) - len(stripped)] + stripped[0].upper() + stripped[1:]
        result.append(line)
    return "\n".join(result)


def normalize(text: str, hedges: bool = True, preambles: bool = True, casual: bool = True) -> str:
    """Normalize Claude output — remove filler, hedges, preambles."""
    if preambles:
        text = _strip_preambles(text)
    if hedges:
        text = _apply_patterns(text, HEDGE_PATTERNS)
    if casual:
        text = _apply_patterns(text, CASUAL_SUBS)
    text = _remove_banned(text)
    text = _capitalize_sentences(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


if __name__ == "__main__":
    sample = """Sure! I'd be happy to help you with that. Here's the complete blog post.

I think this approach is perhaps the most effective way to leverage your data science skills.
However, it's worth noting that kind of workflow might seem somewhat complex at first.
Furthermore, utilizing the right tools makes all the difference — it's a real game-changer.
In conclusion, dive into this framework and you'll see synergy across your entire pipeline."""

    print("=== BEFORE ===")
    print(sample)
    print("\n=== AFTER ===")
    print(normalize(sample))
