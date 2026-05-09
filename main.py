"""
terminology-checker CLI

Usage:
    python main.py <document> <glossary_csv> [--no-ai] [--out OUTPUT_DIR]

Examples:
    python main.py data/sample_document.txt data/glossary_sample.csv
    python main.py data/manual.pdf data/glossary.csv --out output/
    python main.py data/manual.pdf data/glossary.csv --no-ai
"""

import argparse
import sys
from pathlib import Path

from checker.extractor import extract_text, load_glossary
from checker.matcher import find_matches, confirm_with_claude
from checker.reporter import write_csv, write_text, print_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Check terminology violations in a document.")
    parser.add_argument("document", help="Path to document (PDF, DOCX, or TXT)")
    parser.add_argument("glossary", help="Path to glossary CSV")
    parser.add_argument("--no-ai", action="store_true", help="Skip Claude API confirmation step")
    parser.add_argument("--out", default="output", help="Output directory (default: output/)")
    args = parser.parse_args()

    doc_path = Path(args.document)
    glossary_path = Path(args.glossary)
    output_dir = Path(args.out)

    if not doc_path.exists():
        print(f"Error: document not found: {doc_path}", file=sys.stderr)
        sys.exit(1)
    if not glossary_path.exists():
        print(f"Error: glossary not found: {glossary_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Extracting text from: {doc_path.name}")
    text = extract_text(doc_path)
    print(f"  {len(text):,} characters extracted")

    print(f"Loading glossary: {glossary_path.name}")
    glossary = load_glossary(glossary_path)
    print(f"  {len(glossary)} entries loaded")

    print("Running rule-based matching...")
    matches = find_matches(text, glossary)
    print(f"  {len(matches)} candidate violations found")

    if not args.no_ai:
        if matches:
            print("Confirming with Claude API...")
            matches = confirm_with_claude(matches)
        else:
            print("No candidates to confirm.")
    else:
        # Without AI, mark everything as confirmed
        for m in matches:
            m.ai_confirmed = True

    stem = doc_path.stem
    csv_out = output_dir / f"{stem}_violations.csv"
    txt_out = output_dir / f"{stem}_violations.txt"

    write_csv(matches, csv_out)
    write_text(matches, txt_out, source_file=str(doc_path))

    print_summary(matches)
    print(f"Reports saved to:")
    print(f"  {csv_out}")
    print(f"  {txt_out}")


if __name__ == "__main__":
    main()
