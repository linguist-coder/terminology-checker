# Terminology Checker

A Python tool that checks technical documents against a terminology glossary — catching style violations, preferred-term inconsistencies, and duplicate words. Uses Claude AI to filter false positives based on context.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Claude API](https://img.shields.io/badge/Claude-API-orange)
![Gradio](https://img.shields.io/badge/UI-Gradio-purple)

Design notes: [A Rule-First Approach to AI-Assisted Terminology QA](https://www.linguist-coder.com/2026/05/a-rule-first-approach-to-ai-assisted.html) explains why the rules run first and Claude only confirms.

---

## Features

- **Multi-format input** — PDF, DOCX, and plain text
- **CSV glossary** — define wrong terms, preferred replacements, and notes
- **Two-pass detection**
  - Pass 1: regex-based rule matching (fast, no API cost)
  - Pass 2: Claude AI confirmation to filter context-dependent false positives
- **Web UI** — drag-and-drop interface built with Gradio
- **CLI** — scriptable for batch processing
- **CSV report** — downloadable violation list with context and AI reasoning

## Installation

```bash
git clone https://github.com/linguist-coder/terminology-checker.git
cd terminology-checker
pip install -r requirements.txt
```

Set your Anthropic API key:

```bash
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Usage

### Web UI (recommended)

```bash
python app.py
```

Open `http://localhost:7860` in your browser. Upload a document and glossary CSV, then click **Run Check**.

### CLI

```bash
python main.py data/sample_document.pdf data/glossary_sample.csv
```

Options:

| Flag | Description |
|---|---|
| `--no-ai` | Skip Claude API — rule-based detection only |
| `--out DIR` | Output directory (default: `output/`) |

## Glossary Format

Create a CSV file with the following columns:

| Column | Description |
|---|---|
| `wrong_term` | Term to flag (case-insensitive) |
| `correct_term` | Preferred replacement |
| `notes` | Optional explanation shown in the report |

Example:

```csv
wrong_term,correct_term,notes
utilise,use,British spelling — prefer US
in order to,to,verbose phrase
prior to,before,verbose phrase
due to the fact that,because,verbose phrase
```

## Sample Data

| File | Description |
|---|---|
| `data/sample_document.txt` | Plain-text installation guide with embedded violations |
| `data/sample_document.pdf` | PDF version of the same document |
| `data/sample_document.docx` | Word version of the same document |
| `data/glossary_sample.csv` | 17-entry sample glossary |

Generate sample files:

```bash
python data/create_sample_pdf.py
python data/create_sample_docx.py
```

## How It Works

```
Document (PDF / DOCX / TXT)
        │
        ▼
  Text extraction
  (pdfplumber / python-docx)
        │
        ▼
  Rule-based matching          ← regex, word boundary, case-insensitive
  (all glossary terms)
        │
        ▼
  Claude AI confirmation       ← single batched API call
  (context-aware filtering)
        │
        ▼
  Violation report (CSV + TXT)
```

The AI confirmation step sends all candidates in a single API call to minimise cost. On a typical 1,000-word document with a 17-entry glossary, total API cost is under $0.02.

## Tech Stack

- **Python 3.10+**
- **[Anthropic Python SDK](https://github.com/anthropic-ai/anthropic-sdk-python)** — Claude API integration
- **[pdfplumber](https://github.com/jsvine/pdfplumber)** — PDF text extraction
- **[python-docx](https://python-docx.readthedocs.io/)** — Word document extraction
- **[Gradio](https://gradio.app/)** — web UI

## Project Status

MVP complete. Core features working end-to-end.

Planned improvements:
- [ ] Excel glossary support (`.xlsx`)
- [ ] Highlighted output showing violations inline
- [ ] Batch processing for multiple documents

## License

MIT
