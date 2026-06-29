#!/usr/bin/env python
"""Create static reviewer-facing human-audit annotation sheets.

The sheets are generated only from the blinded launch packet. They intentionally
exclude item IDs, models, prompt conditions, and automatic labels.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


LANGUAGE_LABELS = {
    "ar-en": "Arabic-English",
    "es-en": "Spanish-English",
    "hi-en": "Hindi-English",
}
ANNOTATION_FIELDS = [
    "annotator_id",
    "human_pass",
    "human_language_pass",
    "human_script_pass",
    "human_preservation_pass",
    "human_task_pass",
    "human_register_locale_pass",
    "human_failure_types",
    "human_notes",
]
EXPORT_FIELDS = [
    "audit_id",
    "language_pair",
    "task_family",
    "user_prompt",
    "assistant_response",
    "expected_response_language",
    "expected_script",
    "must_preserve_spans",
    "register_requirement",
    "locale_requirement",
    "known_bad_outputs",
    "notes_for_annotators",
    *ANNOTATION_FIELDS,
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sheet_filename(version: str, language_pair: str) -> str:
    return f"human_audit_review_sheet_{version}_{language_pair}.html"


def json_script(rows: list[dict[str, str]]) -> str:
    payload = json.dumps(rows, ensure_ascii=False)
    escaped = payload.replace("</", "<\\/")
    return escaped


def render_sheet(*, version: str, language_pair: str, rows: list[dict[str, str]]) -> str:
    title = f"RePromptTax {version} {LANGUAGE_LABELS[language_pair]} Audit"
    rows_json = json_script(rows)
    export_fields_json = json.dumps(EXPORT_FIELDS)
    annotation_fields_json = json.dumps(ANNOTATION_FIELDS)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #1f2933; background: #f7f9fb; }}
    header {{ padding: 18px 24px; background: #113a5c; color: white; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 18px 20px 32px; }}
    h1 {{ font-size: 22px; margin: 0 0 4px; }}
    h2 {{ font-size: 17px; margin: 28px 0 10px; }}
    label {{ font-weight: 600; display: block; margin-bottom: 4px; }}
    input, select, textarea {{ box-sizing: border-box; width: 100%; border: 1px solid #bcc7d2; border-radius: 4px; padding: 7px; font: inherit; background: white; }}
    textarea {{ min-height: 70px; resize: vertical; }}
    button {{ border: 0; border-radius: 4px; background: #0b6bcb; color: white; padding: 9px 12px; font-weight: 700; cursor: pointer; }}
    button:focus, input:focus, select:focus, textarea:focus {{ outline: 3px solid #9fd0ff; outline-offset: 1px; }}
    .meta {{ color: #d7e6f5; font-size: 13px; }}
    .toolbar {{ display: grid; grid-template-columns: minmax(220px, 1fr) auto; gap: 14px; align-items: end; margin: 16px 0 18px; }}
    .row {{ background: white; border: 1px solid #d5dee8; border-radius: 6px; margin: 14px 0; padding: 16px; }}
    .row-head {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; justify-content: space-between; margin-bottom: 12px; }}
    .pill {{ display: inline-block; border-radius: 999px; background: #e8f1fb; color: #123c5c; padding: 3px 9px; font-size: 12px; font-weight: 700; }}
    .text-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }}
    .field-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-top: 12px; }}
    .wide {{ grid-column: span 3; }}
    .prompt, .response, .constraints {{ white-space: pre-wrap; background: #f9fbfd; border: 1px solid #e1e7ee; border-radius: 4px; padding: 10px; line-height: 1.45; }}
    .constraints {{ margin-top: 10px; }}
    @media (max-width: 780px) {{
      .toolbar, .text-grid, .field-grid {{ grid-template-columns: 1fr; }}
      .wide {{ grid-column: span 1; }}
      main {{ padding: 12px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(title)}</h1>
    <div class="meta">{len(rows)} blinded rows. Export filename: human_audit_packet_{version}_{language_pair}_completed.csv</div>
  </header>
  <main>
    <div class="toolbar">
      <div>
        <label for="annotator_id">Annotator ID</label>
        <input id="annotator_id" autocomplete="off" placeholder="same ID as roster">
      </div>
      <button id="export_button" type="button">Download CSV</button>
    </div>
    <section id="rows"></section>
  </main>
  <script id="audit-data" type="application/json">{rows_json}</script>
  <script>
    const rows = JSON.parse(document.getElementById('audit-data').textContent);
    const exportFields = {export_fields_json};
    const annotationFields = {annotation_fields_json};
    const boolFields = annotationFields.filter((field) => field.startsWith('human_') && field.endsWith('_pass'));

    function optionHtml() {{
      return '<option value=""></option><option value="TRUE">TRUE</option><option value="FALSE">FALSE</option>';
    }}

    function escapeText(value) {{
      return String(value ?? '').replace(/[&<>"']/g, (ch) => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));
    }}

    function fieldId(row, field) {{
      return `${{row.audit_id}}__${{field}}`;
    }}

    function renderRows() {{
      const container = document.getElementById('rows');
      container.innerHTML = rows.map((row) => {{
        const constraints = [
          `Expected language: ${{row.expected_response_language}}`,
          `Expected script: ${{row.expected_script}}`,
          `Preserve exactly: ${{row.must_preserve_spans || '[]'}}`,
          `Known bad outputs: ${{row.known_bad_outputs || '[]'}}`,
          `Register: ${{row.register_requirement || ''}}`,
          `Locale: ${{row.locale_requirement || ''}}`,
          `Notes: ${{row.notes_for_annotators || ''}}`,
        ].join('\\n');
        const boolInputs = boolFields.map((field) => `
          <div>
            <label for="${{fieldId(row, field)}}">${{field.replaceAll('_', ' ')}}</label>
            <select id="${{fieldId(row, field)}}" data-audit-id="${{row.audit_id}}" data-field="${{field}}">${{optionHtml()}}</select>
          </div>
        `).join('');
        return `
          <article class="row">
            <div class="row-head">
              <strong>${{escapeText(row.audit_id)}}</strong>
              <span>
                <span class="pill">${{escapeText(row.language_pair)}}</span>
                <span class="pill">${{escapeText(row.task_family)}}</span>
              </span>
            </div>
            <div class="text-grid">
              <div>
                <label>User prompt</label>
                <div class="prompt">${{escapeText(row.user_prompt)}}</div>
              </div>
              <div>
                <label>Assistant response</label>
                <div class="response">${{escapeText(row.assistant_response)}}</div>
              </div>
            </div>
            <div class="constraints">${{escapeText(constraints)}}</div>
            <div class="field-grid">
              ${{boolInputs}}
              <div class="wide">
                <label for="${{fieldId(row, 'human_failure_types')}}">human failure types</label>
                <input id="${{fieldId(row, 'human_failure_types')}}" data-audit-id="${{row.audit_id}}" data-field="human_failure_types" placeholder="comma-separated, blank if pass">
              </div>
              <div class="wide">
                <label for="${{fieldId(row, 'human_notes')}}">human notes</label>
                <textarea id="${{fieldId(row, 'human_notes')}}" data-audit-id="${{row.audit_id}}" data-field="human_notes"></textarea>
              </div>
            </div>
          </article>
        `;
      }}).join('');
    }}

    function csvEscape(value) {{
      const text = String(value ?? '');
      if (/[",\\n\\r]/.test(text)) {{
        return `"${{text.replaceAll('"', '""')}}"`;
      }}
      return text;
    }}

    function collectRows() {{
      const annotatorId = document.getElementById('annotator_id').value.trim();
      return rows.map((row) => {{
        const out = {{}};
        for (const field of exportFields) {{
          out[field] = row[field] ?? '';
        }}
        out.annotator_id = annotatorId;
        for (const field of annotationFields) {{
          if (field === 'annotator_id') continue;
          const element = document.getElementById(fieldId(row, field));
          out[field] = element ? element.value : '';
        }}
        return out;
      }});
    }}

    function downloadCsv() {{
      const completed = collectRows();
      const lines = [exportFields.join(',')];
      for (const row of completed) {{
        lines.push(exportFields.map((field) => csvEscape(row[field])).join(','));
      }}
      const blob = new Blob([lines.join('\\n') + '\\n'], {{type: 'text/csv;charset=utf-8'}});
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'human_audit_packet_{version}_{language_pair}_completed.csv';
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    }}

    renderRows();
    document.getElementById('export_button').addEventListener('click', downloadCsv);
  </script>
</body>
</html>
"""


def render_index(*, version: str, rows_by_language: dict[str, list[dict[str, str]]]) -> str:
    links = "\n".join(
        f'<li><a href="{html.escape(sheet_filename(version, lang))}">{html.escape(LANGUAGE_LABELS[lang])}</a> ({len(rows)} rows)</li>'
        for lang, rows in sorted(rows_by_language.items())
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RePromptTax {html.escape(version)} Human Audit Sheets</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 880px; margin: 32px auto; padding: 0 18px; line-height: 1.5; color: #1f2933; }}
    a {{ color: #0b6bcb; font-weight: 700; }}
    code {{ background: #edf2f7; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>RePromptTax {html.escape(version)} Human Audit Sheets</h1>
  <p>Send annotators only the sheet for their language pair. The private answer key is not needed for annotation.</p>
  <ul>
    {links}
  </ul>
  <p>Merge completed CSV exports with <code>scripts/merge_review_exports.py</code>, then validate with <code>scripts/validate_completed_human_audit.py</code> after filling the annotator roster.</p>
</body>
</html>
"""


def write_readme(path: Path, *, version: str, packet_dir: Path) -> None:
    text = f"""# Human Audit Review Sheets {version}

These static HTML sheets are generated from the blinded launch packet. They are
for annotation convenience only; the authoritative packet and answer key remain
the CSV files in `{packet_dir}/`.

- Send each annotator only the HTML sheet for their language pair.
- Do not send `human_audit_answer_key_{version}.csv`.
- Ask annotators to enter the same annotator ID that appears in the completed
  roster, fill every TRUE/FALSE field, and download the completed CSV.
- Merge the three completed CSV exports with `scripts/merge_review_exports.py`
  as `{packet_dir}/human_audit_packet_{version}_completed.csv`.
- Validate the completed audit with `scripts/validate_completed_human_audit.py`
  before making any human/native-speaker validation claim.
"""
    write_text(path, text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=Path("data/human_audit/human_audit_packet_v0.2.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("data/human_audit/review_sheets_v0.2"))
    parser.add_argument("--packet-version", default="v0.2")
    args = parser.parse_args()

    rows = read_csv(args.packet)
    require(rows, f"empty packet {args.packet}")
    rows_by_language: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        language_pair = row["language_pair"]
        require(language_pair in LANGUAGE_LABELS, f"unknown language_pair: {language_pair}")
        rows_by_language[language_pair].append(row)

    expected_per_language = len(rows) // len(rows_by_language)
    for language_pair, lang_rows in rows_by_language.items():
        require(len(lang_rows) == expected_per_language, f"{language_pair} expected {expected_per_language} rows, found {len(lang_rows)}")
        write_text(
            args.out_dir / sheet_filename(args.packet_version, language_pair),
            render_sheet(version=args.packet_version, language_pair=language_pair, rows=lang_rows),
        )
    write_text(args.out_dir / "index.html", render_index(version=args.packet_version, rows_by_language=rows_by_language))
    write_readme(args.out_dir / "README.md", version=args.packet_version, packet_dir=args.packet.parent)
    print(f"wrote human-audit review sheets to {args.out_dir}")


if __name__ == "__main__":
    main()
