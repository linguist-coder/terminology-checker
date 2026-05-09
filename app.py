"""
Terminology Checker — Gradio web interface.

Usage:
    python app.py
"""

import os
import tempfile
from pathlib import Path

import gradio as gr

from checker.extractor import extract_text, load_glossary
from checker.matcher import find_matches, confirm_with_claude
from checker.reporter import write_csv


def run_check(
    document_file,
    glossary_file,
    use_ai: bool,
    api_key: str,
):
    """Run the terminology check and return results for display."""
    if document_file is None:
        return "⚠️ Please upload a document.", None
    if glossary_file is None:
        return "⚠️ Please upload a glossary CSV.", None

    # API key: UI field takes priority over env var
    effective_key = api_key.strip() if api_key.strip() else os.environ.get("ANTHROPIC_API_KEY", "")
    if use_ai and not effective_key:
        return (
            "⚠️ Claude AI verification is enabled but no API key was found.  \n"
            "Enter your Anthropic API key above, or set the `ANTHROPIC_API_KEY` environment variable.",
            None,
        )
    if effective_key:
        os.environ["ANTHROPIC_API_KEY"] = effective_key

    try:
        doc_path = Path(document_file)
        glossary_path = Path(glossary_file)

        text = extract_text(doc_path)
        glossary = load_glossary(glossary_path)
        matches = find_matches(text, glossary)

        if use_ai and matches:
            matches = confirm_with_claude(matches)
        else:
            for m in matches:
                m.ai_confirmed = True

        confirmed = [m for m in matches if m.ai_confirmed]
        skipped = len(matches) - len(confirmed)

        # ── Summary ──────────────────────────────────────────────
        ai_label = "Claude AI" if use_ai else "Rule-based only"
        summary_lines = [
            "## Results",
            "",
            f"| | |",
            f"|---|---|",
            f"| Document | `{doc_path.name}` |",
            f"| Glossary entries | {len(glossary)} |",
            f"| Candidates found | {len(matches)} |",
            f"| **Violations confirmed** | **{len(confirmed)}** |",
            f"| Skipped (false positives) | {skipped} |",
            f"| Verification | {ai_label} |",
            "",
        ]

        # ── Violation list ────────────────────────────────────────
        if not confirmed:
            summary_lines.append("✅ **No violations found.**")
        else:
            summary_lines.append("---")
            summary_lines.append("")
            for i, m in enumerate(confirmed, 1):
                summary_lines.append(
                    f"### [{i}] `{m.wrong_term}` → `{m.correct_term}`"
                )
                summary_lines.append("")
                summary_lines.append(f"> {m.context.strip()}")
                summary_lines.append("")
                if m.notes:
                    summary_lines.append(f"**Note:** {m.notes}  ")
                if m.ai_reason:
                    summary_lines.append(f"**AI:** {m.ai_reason}")
                summary_lines.append("")

        result_md = "\n".join(summary_lines)

        # ── CSV download ──────────────────────────────────────────
        tmp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv",
            prefix=f"{doc_path.stem}_violations_",
        )
        tmp.close()
        write_csv(matches, tmp.name)

        return result_md, tmp.name

    except Exception as e:
        return f"❌ Error: {e}", None


# ── UI layout ─────────────────────────────────────────────────────────────────

with gr.Blocks(
    title="Terminology Checker",
    theme=gr.themes.Soft(),
) as demo:

    gr.Markdown(
        """# 📋 Terminology Checker
Check technical documents against your terminology glossary.
Supports **PDF**, **DOCX**, and **TXT** input · Powered by **Claude AI**
"""
    )

    with gr.Row():
        with gr.Column(scale=1):
            doc_input = gr.File(
                label="Document",
                file_types=[".pdf", ".docx", ".txt"],
                file_count="single",
            )
            glossary_input = gr.File(
                label="Glossary (CSV)",
                file_types=[".csv"],
                file_count="single",
            )

        with gr.Column(scale=1):
            use_ai = gr.Checkbox(
                label="Use Claude AI for context verification",
                value=True,
                info="Filters false positives using the Claude API. Requires an API key.",
            )
            api_key_input = gr.Textbox(
                label="Anthropic API Key",
                type="password",
                placeholder="sk-ant-...   (or set ANTHROPIC_API_KEY env var)",
            )
            gr.Markdown(
                "<small>Your key is used only for this session and never stored.</small>"
            )
            run_btn = gr.Button("▶ Run Check", variant="primary", size="lg")

    results_output = gr.Markdown(label="Results")
    download_output = gr.File(label="Download CSV Report", visible=True)

    run_btn.click(
        fn=run_check,
        inputs=[doc_input, glossary_input, use_ai, api_key_input],
        outputs=[results_output, download_output],
    )

    gr.Markdown(
        "---\n*Built with Python + Claude API · "
        "[View source on GitHub](https://github.com/)*"
    )


if __name__ == "__main__":
    demo.launch()
