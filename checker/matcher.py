"""Term matching: rule-based detection + Claude API contextual judgment."""

import re
import os
from dataclasses import dataclass, field

import anthropic

from .extractor import GlossaryEntry


@dataclass
class Match:
    wrong_term: str
    correct_term: str
    context: str        # surrounding sentence
    position: int       # char offset in document
    notes: str
    ai_confirmed: bool = False
    ai_reason: str = ""


def find_matches(text: str, glossary: list[GlossaryEntry]) -> list[Match]:
    """Rule-based pass: find all occurrences of wrong terms."""
    matches = []
    sentences = _split_sentences(text)

    for entry in glossary:
        if not entry.wrong_term:
            continue
        pattern = re.compile(r'\b' + re.escape(entry.wrong_term) + r'\b', re.IGNORECASE)
        for sentence in sentences:
            for m in pattern.finditer(sentence):
                matches.append(Match(
                    wrong_term=entry.wrong_term,
                    correct_term=entry.correct_term,
                    context=sentence.strip(),
                    position=m.start(),
                    notes=entry.notes,
                ))

    return matches


def confirm_with_claude(matches: list[Match], model: str = "claude-sonnet-4-6") -> list[Match]:
    """Claude API pass: filter false positives and add explanations."""
    if not matches:
        return matches

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # Build a single batched prompt to minimise API calls
    items = "\n".join(
        f"{i+1}. Wrong: \"{m.wrong_term}\" | Preferred: \"{m.correct_term}\" | "
        f"Context: \"{m.context}\""
        for i, m in enumerate(matches)
    )

    static_instructions = (
        "You are a technical writing style reviewer.\n"
        "For each item below, decide whether the flagged term is actually used incorrectly in context.\n"
        "Reply with a JSON array. Each element must have:\n"
        '  "index": 1-based number matching the item\n'
        '  "confirmed": true if this is a genuine style violation, false if it is acceptable in context\n'
        '  "reason": one short sentence explaining your decision\n\n'
        "Items:\n"
    )

    response = client.beta.messages.create(
        model=model,
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": "You are a precise technical writing reviewer. Respond only with valid JSON.",
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": static_instructions,
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": items + "\n\nReturn only the JSON array, no extra text.",
                    },
                ],
            }
        ],
        betas=["prompt-caching-2024-07-31"],
    )

    usage = response.usage
    cache_creation = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    print(f"  [API] input: {usage.input_tokens} tokens / output: {usage.output_tokens} tokens")
    print(f"  [Cache] created: {cache_creation} / read: {cache_read}")

    import json
    try:
        raw = response.content[0].text.strip()
        # Strip markdown code fences if present (e.g. ```json ... ```)
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw.strip())
        results = json.loads(raw)
        for r in results:
            idx = r["index"] - 1
            if 0 <= idx < len(matches):
                matches[idx].ai_confirmed = r.get("confirmed", True)
                matches[idx].ai_reason = r.get("reason", "")
    except (json.JSONDecodeError, KeyError, IndexError):
        # If parsing fails, mark all as confirmed to avoid silent data loss
        for m in matches:
            m.ai_confirmed = True
            m.ai_reason = "AI response parse error — manual review recommended"

    return matches


def _split_sentences(text: str) -> list[str]:
    # Simple sentence splitter; good enough for PoC
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p for p in parts if p.strip()]
