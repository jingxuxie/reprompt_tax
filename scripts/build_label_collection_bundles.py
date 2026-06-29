#!/usr/bin/env python
"""Build sendable reviewer bundles for launch-ready label collection."""

from __future__ import annotations

import argparse
import csv
import hashlib
import zipfile
from pathlib import Path
from typing import Any


OUT_DIR = Path("results/label_collection_bundles_v02")

HUMAN_SLICES = {
    "ar-en": "Arabic-English",
    "es-en": "Spanish-English",
    "hi-en": "Hindi-English",
}

COVERAGE_SLICES = {
    "arabic_instruction_arabic_filenames": "Arabic Instruction, Arabic Content With English File Names",
    "english_instruction_arabic_content": "English Instruction, Arabic Content",
    "english_instruction_hindi_content": "English Instruction, Hindi Content",
    "english_instruction_spanish_content": "English Instruction, Spanish Content",
    "hindi_english_instruction_hindi_devanagari": "Hindi-English Instruction, Hindi Devanagari Content",
    "spanish_instruction_arabic_quote": "Spanish Instruction, Arabic Quote",
}

PRIVATE_MARKERS = (
    "answer_key",
    "auto_pass",
    "auto_language_pass",
    "auto_script_pass",
    "auto_preservation_pass",
    "auto_task_pass",
    "auto_register_locale_pass",
    "auto_failure_types",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(rows, "refusing to write empty bundle manifest")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def zip_bytes(path: Path, arcname: str, payload: bytes) -> None:
    info = zipfile.ZipInfo(arcname)
    info.date_time = (2026, 1, 1, 0, 0, 0)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    with zipfile.ZipFile(path, "a") as zf:
        zf.writestr(info, payload)


def check_sendable_text(text: str, *, path: Path) -> None:
    lowered = text.lower()
    for marker in PRIVATE_MARKERS:
        require(marker not in lowered, f"{path} contains private marker {marker}")
    require("model" not in lowered, f"{path} contains model marker")
    require("condition" not in lowered, f"{path} contains condition marker")


def human_readme(*, title: str, expected_export_name: str) -> str:
    return f"""# RePromptTax Human Audit Bundle

Slice: {title}

Files:

- `review_sheet.html`: preferred local browser interface.
- `slice_packet.csv`: equivalent CSV packet if you prefer spreadsheet editing.
- `review_instructions.md`: labeling rules and failure-type codes.

Use the reviewer or annotator ID assigned in the roster. Fill every TRUE/FALSE
field. If any component is FALSE, include the matching failure type. Export or
save the completed CSV as `{expected_export_name}`.

This bundle intentionally excludes private answer keys, model names, prompt
conditions, and automatic labels.
"""


def coverage_readme(*, title: str, expected_export_name: str) -> str:
    return f"""# RePromptTax v0.3 Coverage Native-Review Bundle

Slice: {title}

Files:

- `review_sheet.html`: preferred local browser interface.
- `slice_packet.csv`: equivalent CSV packet if you prefer spreadsheet editing.
- `review_instructions.md`: labeling rules and issue-type codes.

Use the reviewer ID assigned in the roster. Fill every TRUE/FALSE field. If any
component is FALSE, include the matching issue type. Export or save the
completed CSV as `{expected_export_name}`.

This bundle intentionally excludes model-output scores and automatic labels.
"""


HUMAN_INSTRUCTIONS = """# Human Audit Instructions

Mark `human_pass` TRUE only when all component labels are TRUE.

Failure-type mapping:

- `human_language_pass` FALSE -> `wrong_output_language`
- `human_script_pass` FALSE -> `script_mismatch`
- `human_preservation_pass` FALSE -> `preservation_failure`
- `human_task_pass` FALSE -> `task_noncompletion`
- `human_register_locale_pass` FALSE -> `register_locale_mismatch`

Do not list a failure type for a component marked TRUE. Use `other` only with a
short note.
"""

COVERAGE_INSTRUCTIONS = """# v0.3 Coverage Native-Review Instructions

Mark `reviewer_release_usable` TRUE only when all component labels are TRUE.

Issue-type mapping:

- `reviewer_prompt_clear` FALSE -> `ambiguous_instruction`
- `reviewer_target_language_natural` FALSE -> `unnatural_target_text`
- `reviewer_script_expectation_valid` FALSE -> `script_expectation_problem`
- `reviewer_preservation_spans_valid` FALSE -> `preservation_span_problem`
- `reviewer_known_bad_outputs_valid` FALSE -> `known_bad_output_problem`

Do not list an issue type for a component marked TRUE. Use `other` only with a
short note.
"""


def build_zip(*, out_path: Path, readme: str, instructions: str, csv_path: Path, html_path: Path) -> None:
    require(csv_path.exists(), f"missing bundle CSV {csv_path}")
    require(html_path.exists(), f"missing bundle HTML {html_path}")
    csv_text = csv_path.read_text(encoding="utf-8")
    html_text = html_path.read_text(encoding="utf-8")
    check_sendable_text(csv_text, path=csv_path)
    check_sendable_text(html_text, path=html_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()
    zip_bytes(out_path, "README.md", readme.encode("utf-8"))
    zip_bytes(out_path, "review_instructions.md", instructions.encode("utf-8"))
    zip_bytes(out_path, "slice_packet.csv", csv_text.encode("utf-8"))
    zip_bytes(out_path, "review_sheet.html", html_text.encode("utf-8"))


def human_surfaces() -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    for surface_id, packet_dir, version, row_count in (
        ("human_audit_v02", Path("data/human_audit"), "v0.2", 24),
        ("current_model_human_audit_v02", Path("data/current_model_human_audit"), "v0.2_current_gpt5", 16),
    ):
        for language_pair, title in HUMAN_SLICES.items():
            surfaces.append(
                {
                    "surface_id": surface_id,
                    "slice_id": language_pair,
                    "title": title,
                    "mode": "human_audit",
                    "expected_rows": row_count,
                    "expected_export_name": f"human_audit_packet_{version}_{language_pair}_completed.csv",
                    "csv_path": packet_dir / f"human_audit_packet_{version}_{language_pair}.csv",
                    "html_path": packet_dir / f"review_sheets_{version}" / f"human_audit_review_sheet_{version}_{language_pair}.html",
                    "instructions": HUMAN_INSTRUCTIONS,
                }
            )
    return surfaces


def coverage_surfaces() -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    packet_dir = Path("data/coverage_native_review_v03")
    for coverage_slice, title in COVERAGE_SLICES.items():
        surfaces.append(
            {
                "surface_id": "coverage_native_review_v03",
                "slice_id": coverage_slice,
                "title": title,
                "mode": "coverage_native_review",
                "expected_rows": 10,
                "expected_export_name": f"coverage_native_review_v03_{coverage_slice}_completed.csv",
                "csv_path": packet_dir / f"coverage_native_review_v03_{coverage_slice}.csv",
                "html_path": packet_dir / "review_sheets_v03" / f"coverage_native_review_sheet_v03_{coverage_slice}.html",
                "instructions": COVERAGE_INSTRUCTIONS,
            }
        )
    return surfaces


def build_bundles(out_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for surface in [*human_surfaces(), *coverage_surfaces()]:
        csv_rows = read_csv(surface["csv_path"])
        require(len(csv_rows) == surface["expected_rows"], f"{surface['csv_path']} expected {surface['expected_rows']} rows")
        bundle_path = out_dir / surface["surface_id"] / f"{surface['slice_id']}.zip"
        readme = (
            human_readme(title=surface["title"], expected_export_name=surface["expected_export_name"])
            if surface["mode"] == "human_audit"
            else coverage_readme(title=surface["title"], expected_export_name=surface["expected_export_name"])
        )
        build_zip(
            out_path=bundle_path,
            readme=readme,
            instructions=surface["instructions"],
            csv_path=surface["csv_path"],
            html_path=surface["html_path"],
        )
        rows.append(
            {
                "surface_id": surface["surface_id"],
                "slice_id": surface["slice_id"],
                "mode": surface["mode"],
                "title": surface["title"],
                "expected_rows": surface["expected_rows"],
                "expected_export_name": surface["expected_export_name"],
                "bundle_path": str(bundle_path),
                "bytes": bundle_path.stat().st_size,
                "sha256": sha256_file(bundle_path),
            }
        )
    return rows


def write_report(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Label Collection Reviewer Bundles",
        "",
        "These zip files are sendable reviewer packages generated from blinded",
        "slice packets and static review sheets. They intentionally exclude",
        "answer keys, model names, prompt conditions, and automatic labels.",
        "",
        "| Surface | Slice | Rows | Bundle |",
        "|---|---|---:|---|",
    ]
    for row in rows:
        lines.append(f"| {row['surface_id']} | {row['slice_id']} | {row['expected_rows']} | `{row['bundle_path']}` |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    rows = build_bundles(args.out_dir)
    write_csv(args.out_dir / "label_collection_bundle_manifest.csv", rows)
    write_report(args.out_dir / "label_collection_bundles.md", rows)
    print(f"wrote {len(rows)} label-collection reviewer bundles to {args.out_dir}")


if __name__ == "__main__":
    main()
