"""Generate violation reports in CSV and plain-text formats."""

import csv
from pathlib import Path
from datetime import datetime

from .matcher import Match


def write_csv(matches: list[Match], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    confirmed = [m for m in matches if m.ai_confirmed]

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["#", "Wrong Term", "Correct Term", "Context", "Notes", "AI Reason"])
        for i, m in enumerate(confirmed, 1):
            writer.writerow([i, m.wrong_term, m.correct_term, m.context, m.notes, m.ai_reason])

    return path


def write_text(matches: list[Match], output_path: str | Path, source_file: str = "") -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    confirmed = [m for m in matches if m.ai_confirmed]
    skipped = len(matches) - len(confirmed)

    lines = [
        "=" * 60,
        "TERMINOLOGY CHECKER — VIOLATION REPORT",
        f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ]
    if source_file:
        lines.append(f"Source    : {source_file}")
    lines += [
        f"Violations: {len(confirmed)}  (skipped by AI: {skipped})",
        "=" * 60,
        "",
    ]

    for i, m in enumerate(confirmed, 1):
        lines += [
            f"[{i}] \"{m.wrong_term}\"  →  \"{m.correct_term}\"",
            f"    Context : {m.context}",
        ]
        if m.notes:
            lines.append(f"    Note    : {m.notes}")
        if m.ai_reason:
            lines.append(f"    AI      : {m.ai_reason}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def print_summary(matches: list[Match]) -> None:
    confirmed = [m for m in matches if m.ai_confirmed]
    skipped = len(matches) - len(confirmed)

    print(f"\n{'='*60}")
    print(f"  Violations confirmed : {len(confirmed)}")
    print(f"  Skipped by AI        : {skipped}")
    print(f"{'='*60}\n")

    for i, m in enumerate(confirmed, 1):
        print(f"[{i}] \"{m.wrong_term}\"  →  \"{m.correct_term}\"")
        print(f"    {m.context}")
        if m.ai_reason:
            print(f"    AI: {m.ai_reason}")
        print()
