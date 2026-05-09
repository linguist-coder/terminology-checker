"""Text extraction from PDF, Word, and plain text files."""

import csv
from pathlib import Path
from dataclasses import dataclass


@dataclass
class GlossaryEntry:
    wrong_term: str
    correct_term: str
    notes: str


def extract_text(file_path: str | Path) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(path)
    elif suffix in (".docx", ".doc"):
        return _extract_docx(path)
    elif suffix == ".txt":
        return path.read_text(encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _extract_pdf(path: Path) -> str:
    import pdfplumber

    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
    return "\n".join(pages)


def _extract_docx(path: Path) -> str:
    from docx import Document

    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def load_glossary(csv_path: str | Path) -> list[GlossaryEntry]:
    entries = []
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            wrong = row.get("wrong_term", "").strip()
            if wrong:
                entries.append(GlossaryEntry(
                    wrong_term=wrong,
                    correct_term=row.get("correct_term", "").strip(),
                    notes=row.get("notes", "").strip(),
                ))
    return entries
