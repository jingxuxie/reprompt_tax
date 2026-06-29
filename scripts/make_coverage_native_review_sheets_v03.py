#!/usr/bin/env python
"""Create static reviewer-facing sheets for the v0.3 native-review packet."""

from __future__ import annotations

import argparse
import csv
import html
import json
from collections import defaultdict
from pathlib import Path

from make_coverage_native_review_packet_v03 import EXPECTED_SLICES, PACKET_FIELDS, REVIEW_FIELDS


SLICE_LABELS = {
    "arabic_instruction_arabic_filenames": "Arabic Instruction, Arabic Content With English File Names",
    "english_instruction_arabic_content": "English Instruction, Arabic Content",
    "english_instruction_hindi_content": "English Instruction, Hindi Content",
    "english_instruction_spanish_content": "English Instruction, Spanish Content",
    "hindi_english_instruction_hindi_devanagari": "Hindi-English Instruction, Hindi Devanagari Content",
    "spanish_instruction_arabic_quote": "Spanish Instruction, Arabic Quote",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sheet_filename(coverage_slice: str) -> str:
    return f"coverage_native_review_sheet_v03_{coverage_slice}.html"


def json_script(rows: list[dict[str, str]]) -> str:
    payload = json.dumps(rows, ensure_ascii=False)
    return payload.replace("</", "<\\/")


def render_sheet(*, coverage_slice: str, rows: list[dict[str, str]]) -> str:
    title = f"RePromptTax v0.3 Native Review: {SLICE_LABELS[coverage_slice]}"
    rows_json = json_script(rows)
    export_fields_json = json.dumps(PACKET_FIELDS)
    review_fields_json = json.dumps(REVIEW_FIELDS)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #1f2933; background: #f7f9fb; }}
    header {{ padding: 18px 24px; background: #23424f; color: white; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 18px 20px 32px; }}
    h1 {{ font-size: 22px; margin: 0 0 4px; }}
    label {{ font-weight: 600; display: block; margin-bottom: 4px; }}
    input, select, textarea {{ box-sizing: border-box; width: 100%; border: 1px solid #bcc7d2; border-radius: 4px; padding: 7px; font: inherit; background: white; }}
    textarea {{ min-height: 72px; resize: vertical; }}
    button {{ border: 0; border-radius: 4px; background: #0b6bcb; color: white; padding: 9px 12px; font-weight: 700; cursor: pointer; }}
    button:focus, input:focus, select:focus, textarea:focus {{ outline: 3px solid #9fd0ff; outline-offset: 1px; }}
    .meta {{ color: #e1eef5; font-size: 13px; }}
    .toolbar {{ display: grid; grid-template-columns: minmax(220px, 1fr) auto; gap: 14px; align-items: end; margin: 16px 0 18px; }}
    .row {{ background: white; border: 1px solid #d5dee8; border-radius: 6px; margin: 14px 0; padding: 16px; }}
    .row-head {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; justify-content: space-between; margin-bottom: 12px; }}
    .pill {{ display: inline-block; border-radius: 999px; background: #e8f1fb; color: #123c5c; padding: 3px 9px; font-size: 12px; font-weight: 700; }}
    .text-grid {{ display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 14px; }}
    .field-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-top: 12px; }}
    .wide {{ grid-column: span 3; }}
    .prompt, .constraints {{ white-space: pre-wrap; background: #f9fbfd; border: 1px solid #e1e7ee; border-radius: 4px; padding: 10px; line-height: 1.45; }}
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
    <div class="meta">{len(rows)} launch rows. Export filename: coverage_native_review_v03_{html.escape(coverage_slice)}_completed.csv</div>
  </header>
  <main>
    <div class="toolbar">
      <div>
        <label for="reviewer_id">Reviewer ID</label>
        <input id="reviewer_id" autocomplete="off" placeholder="same ID as roster">
      </div>
      <button id="export_button" type="button">Download CSV</button>
    </div>
    <section id="rows"></section>
  </main>
  <script id="review-data" type="application/json">{rows_json}</script>
  <script>
    const rows = JSON.parse(document.getElementById('review-data').textContent);
    const exportFields = {export_fields_json};
    const reviewFields = {review_fields_json};
    const boolFields = reviewFields.filter((field) => field.startsWith('reviewer_') && !['reviewer_id', 'reviewer_issue_types', 'reviewer_notes'].includes(field));

    function optionHtml() {{
      return '<option value=""></option><option value="TRUE">TRUE</option><option value="FALSE">FALSE</option>';
    }}

    function escapeText(value) {{
      return String(value ?? '').replace(/[&<>"']/g, (ch) => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));
    }}

    function fieldId(row, field) {{
      return `${{row.review_id}}__${{field}}`;
    }}

    function renderRows() {{
      const container = document.getElementById('rows');
      container.innerHTML = rows.map((row) => {{
        const constraints = [
          `Expected response language: ${{row.expected_response_language}}`,
          `Expected script: ${{row.expected_script}}`,
          `Preserve exactly: ${{row.must_preserve_spans || '[]'}}`,
          `Required markers: ${{row.required_any_markers || '[]'}}`,
          `Forbidden markers: ${{row.forbidden_markers || '[]'}}`,
          `Known bad outputs: ${{row.known_bad_outputs || '[]'}}`,
          `Register: ${{row.register_requirement || ''}}`,
          `Locale: ${{row.locale_requirement || ''}}`,
          `Notes: ${{row.notes_for_reviewers || ''}}`,
        ].join('\\n');
        const boolInputs = boolFields.map((field) => `
          <div>
            <label for="${{fieldId(row, field)}}">${{field.replaceAll('_', ' ')}}</label>
            <select id="${{fieldId(row, field)}}" data-review-id="${{row.review_id}}" data-field="${{field}}">${{optionHtml()}}</select>
          </div>
        `).join('');
        return `
          <article class="row">
            <div class="row-head">
              <strong>${{escapeText(row.review_id)}}</strong>
              <span>
                <span class="pill">${{escapeText(row.coverage_slice)}}</span>
                <span class="pill">${{escapeText(row.language_pair)}}</span>
                <span class="pill">${{escapeText(row.content_language)}}</span>
              </span>
            </div>
            <div class="text-grid">
              <div>
                <label>User prompt</label>
                <div class="prompt">${{escapeText(row.user_prompt)}}</div>
              </div>
              <div>
                <label>Review constraints</label>
                <div class="constraints">${{escapeText(constraints)}}</div>
              </div>
            </div>
            <div class="field-grid">
              ${{boolInputs}}
              <div class="wide">
                <label for="${{fieldId(row, 'reviewer_issue_types')}}">reviewer issue types</label>
                <input id="${{fieldId(row, 'reviewer_issue_types')}}" data-review-id="${{row.review_id}}" data-field="reviewer_issue_types" placeholder="comma-separated, blank if release usable">
              </div>
              <div class="wide">
                <label for="${{fieldId(row, 'reviewer_notes')}}">reviewer notes</label>
                <textarea id="${{fieldId(row, 'reviewer_notes')}}" data-review-id="${{row.review_id}}" data-field="reviewer_notes"></textarea>
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
      const reviewerId = document.getElementById('reviewer_id').value.trim();
      return rows.map((row) => {{
        const out = {{}};
        for (const field of exportFields) {{
          out[field] = row[field] ?? '';
        }}
        out.reviewer_id = reviewerId;
        for (const field of reviewFields) {{
          if (field === 'reviewer_id') continue;
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
      link.download = 'coverage_native_review_v03_{coverage_slice}_completed.csv';
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


def render_index(rows_by_slice: dict[str, list[dict[str, str]]]) -> str:
    links = "\n".join(
        f'<li><a href="{html.escape(sheet_filename(coverage_slice))}">{html.escape(SLICE_LABELS[coverage_slice])}</a> ({len(rows)} rows)</li>'
        for coverage_slice, rows in sorted(rows_by_slice.items())
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RePromptTax v0.3 Coverage Native Review Sheets</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 920px; margin: 32px auto; padding: 0 18px; line-height: 1.5; color: #1f2933; }}
    a {{ color: #0b6bcb; font-weight: 700; }}
    code {{ background: #edf2f7; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>RePromptTax v0.3 Coverage Native Review Sheets</h1>
  <p>Send reviewers only the sheet for their qualified coverage slice. Use two independent reviewers per slice when possible.</p>
  <ul>
    {links}
  </ul>
  <p>Merge completed CSV exports with <code>scripts/merge_review_exports.py</code>, then validate with <code>scripts/validate_completed_coverage_native_review_v03.py</code> after finalization, or first adjudicate with <code>scripts/analyze_coverage_native_review_adjudication.py</code> when two independent rows per item are collected.</p>
</body>
</html>
"""


def write_readme(path: Path, *, packet_dir: Path) -> None:
    text = f"""# v0.3 Coverage Native-Review Sheets

These static HTML sheets are generated from the v0.3 coverage native-review
launch packet. They are for reviewer convenience only; the authoritative packet
and roster remain the CSV files in `{packet_dir}/`.

- Send each reviewer only the HTML sheet for their qualified coverage slice.
- Ask reviewers to enter the same reviewer ID that appears in the completed
  roster, fill every TRUE/FALSE field, and download the completed CSV.
- Prefer two independent reviewers per slice. Merge their completed CSV exports
  with `scripts/merge_review_exports.py --labels-per-item 2` as
  `coverage_native_review_packet_v03_double_completed.csv`, keeping duplicate
  `review_id` values and unique `reviewer_id` values.
- Run `scripts/analyze_coverage_native_review_adjudication.py`, fill the
  generated disagreement packet, then run
  `scripts/finalize_coverage_native_review_adjudication.py`.
- Validate finalized one-row-per-item labels with
  `scripts/validate_completed_coverage_native_review_v03.py` before making any
  completed-native-validation claim.
"""
    write_text(path, text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=Path("data/coverage_native_review_v03/coverage_native_review_packet_v03.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("data/coverage_native_review_v03/review_sheets_v03"))
    args = parser.parse_args()

    rows = read_csv(args.packet)
    require(rows, f"empty packet {args.packet}")
    rows_by_slice: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        coverage_slice = row["coverage_slice"]
        require(coverage_slice in EXPECTED_SLICES, f"unknown coverage_slice: {coverage_slice}")
        rows_by_slice[coverage_slice].append(row)

    require(set(rows_by_slice) == set(EXPECTED_SLICES), "coverage-review sheets do not cover all expected slices")
    for coverage_slice, slice_rows in rows_by_slice.items():
        require(len(slice_rows) == 10, f"{coverage_slice} expected 10 rows, found {len(slice_rows)}")
        write_text(
            args.out_dir / sheet_filename(coverage_slice),
            render_sheet(coverage_slice=coverage_slice, rows=slice_rows),
        )
    write_text(args.out_dir / "index.html", render_index(rows_by_slice))
    write_readme(args.out_dir / "README.md", packet_dir=args.packet.parent)
    print(f"wrote v0.3 coverage native-review sheets to {args.out_dir}")


if __name__ == "__main__":
    main()
