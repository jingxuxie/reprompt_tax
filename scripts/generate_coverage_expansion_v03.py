#!/usr/bin/env python
"""Generate a synthetic v0.3 coverage expansion scaffold.

This file intentionally creates a separate scaffold instead of mutating the
paper-facing v0.2 benchmark. The rows broaden non-English target-content
editing coverage, but they are not model results and require native-speaker
review before claim-bearing use.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


OUTPUT_PATH = Path("data/benchmark_stress_v0.3_expansion.jsonl")
VERSION = "v0.3-expansion-scaffold"
VALIDATION_STATUS = "synthetic_scaffold_requires_native_validation"

SPANISH_ITEMS = [
    ("El equipo terminó el informe, pero falta revisar la conclusión antes de enviarlo.", ["informe", "conclusión"]),
    ("La biblioteca abrirá más temprano el lunes porque hay una sesión de lectura.", ["biblioteca", "sesión de lectura"]),
    ("El cliente aprobó el diseño, aunque pidió cambios en la portada.", ["cliente", "portada"]),
    ("La clase avanzó con el proyecto, pero el resumen final necesita ejemplos.", ["proyecto", "resumen final"]),
    ("La campaña llegó a nuevos grupos y recibió comentarios sobre el calendario.", ["campaña", "calendario"]),
    ("La oficina confirmó la reunión, pero el presupuesto todavía está pendiente.", ["reunión", "presupuesto"]),
    ("El instructor explicó el tratamiento del tema y pidió registrar dudas diarias.", ["instructor", "dudas diarias"]),
    ("La tienda actualizó el inventario y reservó más espacio para productos locales.", ["inventario", "productos locales"]),
    ("El museo publicó el programa y añadió una visita guiada por la tarde.", ["programa", "visita guiada"]),
    ("La organización cerró la encuesta y compartirá los resultados en agosto.", ["encuesta", "resultados"]),
]

HINDI_ITEMS = [
    ("टीम ने मसौदा पूरा कर लिया है, लेकिन निष्कर्ष अभी कमजोर लग रहा है।", ["मसौदा", "निष्कर्ष"]),
    ("पुस्तकालय सोमवार को जल्दी खुलेगा क्योंकि पढ़ने का सत्र रखा गया है।", ["पुस्तकालय", "पढ़ने का सत्र"]),
    ("ग्राहक ने डिजाइन स्वीकार किया, पर आवरण में बदलाव मांगे हैं।", ["ग्राहक", "आवरण"]),
    ("कक्षा ने परियोजना पर काम बढ़ाया, लेकिन अंतिम सारांश में उदाहरण चाहिए।", ["परियोजना", "अंतिम सारांश"]),
    ("अभियान नए परिवारों तक पहुँचा और कैलेंडर पर सुझाव मिले।", ["अभियान", "कैलेंडर"]),
    ("कार्यालय ने बैठक की पुष्टि की, लेकिन बजट अभी तय नहीं हुआ है।", ["बैठक", "बजट"]),
    ("शिक्षक ने अभ्यास समझाया और दैनिक प्रगति लिखने को कहा।", ["अभ्यास", "दैनिक प्रगति"]),
    ("दुकान ने भंडार अपडेट किया और स्थानीय उत्पादों के लिए जगह रखी।", ["भंडार", "स्थानीय उत्पादों"]),
    ("संग्रहालय ने कार्यक्रम जारी किया और शाम की निर्देशित यात्रा जोड़ी।", ["कार्यक्रम", "निर्देशित यात्रा"]),
    ("संस्था ने सर्वेक्षण बंद किया और अगस्त में परिणाम साझा करेगी।", ["सर्वेक्षण", "परिणाम"]),
]

ARABIC_ITEMS = [
    ("أنهى الفريق المسودة، لكن الخاتمة تحتاج إلى توضيح قبل الإرسال.", ["المسودة", "الخاتمة"]),
    ("ستفتح المكتبة مبكرا يوم الاثنين لأن جلسة القراءة ستبدأ صباحا.", ["المكتبة", "جلسة القراءة"]),
    ("وافق العميل على التصميم، لكنه طلب تعديلات في الغلاف.", ["العميل", "الغلاف"]),
    ("تقدم الصف في المشروع، لكن الملخص النهائي يحتاج إلى أمثلة.", ["المشروع", "الملخص النهائي"]),
    ("وصلت الحملة إلى عائلات جديدة وتلقت ملاحظات حول التقويم.", ["الحملة", "التقويم"]),
    ("أكد المكتب موعد الاجتماع، لكن الميزانية لم تعتمد بعد.", ["الاجتماع", "الميزانية"]),
    ("شرح المعلم التمرين وطلب تسجيل التقدم اليومي.", ["التمرين", "التقدم اليومي"]),
    ("حدث المتجر المخزون وخصص مساحة للمنتجات المحلية.", ["المخزون", "المنتجات المحلية"]),
    ("نشر المتحف البرنامج وأضاف جولة إرشادية في المساء.", ["البرنامج", "جولة إرشادية"]),
    ("أغلقت المؤسسة الاستبيان وستشارك النتائج في أغسطس.", ["الاستبيان", "النتائج"]),
]

ARABIC_FILENAME_ITEMS = [
    (
        "راجعت ملف budget_plan.xlsx، لكن ملخص presentation_draft.pptx يحتاج إلى تعديل قبل الاجتماع.",
        ["budget_plan.xlsx", "presentation_draft.pptx"],
    ),
    (
        "حفظ الفريق ملاحظات workshop_notes.docx، وينتظر مراجعة chart_update.png قبل النشر.",
        ["workshop_notes.docx", "chart_update.png"],
    ),
    (
        "يحتوي folder_map.csv على أسماء الأقسام، لكن staffing_overview.pdf يحتاج إلى فقرة افتتاحية.",
        ["folder_map.csv", "staffing_overview.pdf"],
    ),
    (
        "أرسلت لي نسخة survey_results.xlsx، لكن response_summary.docx لا يشرح سبب التغيير.",
        ["survey_results.xlsx", "response_summary.docx"],
    ),
    (
        "تطابق cost_table.csv مع العرض، لكن launch_brief.pptx يحتاج إلى ترتيب أوضح.",
        ["cost_table.csv", "launch_brief.pptx"],
    ),
    (
        "سجلت الملاحظات في design_notes.docx، وبقيت صورة banner_mockup.png بحاجة إلى وصف قصير.",
        ["design_notes.docx", "banner_mockup.png"],
    ),
    (
        "راجعنا ملف agenda_final.docx، لكن checklist_grid.xlsx لا يذكر خطوة المتابعة.",
        ["agenda_final.docx", "checklist_grid.xlsx"],
    ),
    (
        "يشرح market_outline.pdf الفكرة العامة، لكن demo_script.docx يحتاج إلى خاتمة أبسط.",
        ["market_outline.pdf", "demo_script.docx"],
    ),
    (
        "تضمين صورة route_map.png مناسب، لكن report_draft.pdf يحتاج إلى عنوان أوضح.",
        ["route_map.png", "report_draft.pdf"],
    ),
    (
        "يوضح ملف training_plan.docx الأهداف، لكن quiz_items.csv يحتاج إلى أمثلة إضافية.",
        ["training_plan.docx", "quiz_items.csv"],
    ),
]


SLICE_SPECS = [
    {
        "coverage_slice": "english_instruction_spanish_content",
        "id_prefix": "v03_en_es_EP",
        "language_pair": "en-es",
        "instruction_language": "English",
        "content_language": "Spanish",
        "expected_response_language": "Spanish",
        "expected_script": "Latin",
        "items": SPANISH_ITEMS,
        "prompt_template": (
            'Please polish this Spanish update while keeping the answer in Spanish '
            'and not translating it into English: "{text}"'
        ),
        "repair_prompt_1": "Please keep the polished answer in Spanish.",
        "repair_prompt_2": "Do not translate into English. Output only the polished Spanish text.",
        "forbidden_markers": ["Here is", "The team", "بالطبع", "إليك", "प्रिय", "नमस्ते"],
        "notes": "English instruction with Spanish target content; preserves the target language.",
    },
    {
        "coverage_slice": "english_instruction_hindi_content",
        "id_prefix": "v03_en_hi_EP",
        "language_pair": "en-hi",
        "instruction_language": "English",
        "content_language": "Hindi",
        "expected_response_language": "Hindi",
        "expected_script": "Devanagari",
        "items": HINDI_ITEMS,
        "prompt_template": (
            'Please polish this Hindi note while keeping the answer in Hindi Devanagari '
            'and not translating it into English: "{text}"'
        ),
        "repair_prompt_1": "Please keep the polished answer in Hindi Devanagari.",
        "repair_prompt_2": "Do not translate into English. Output only the polished Hindi text.",
        "forbidden_markers": ["Here is", "Claro", "بالطبع", "إليك"],
        "notes": "English instruction with Hindi Devanagari target content.",
    },
    {
        "coverage_slice": "english_instruction_arabic_content",
        "id_prefix": "v03_en_ar_EP",
        "language_pair": "en-ar",
        "instruction_language": "English",
        "content_language": "Arabic",
        "expected_response_language": "Arabic",
        "expected_script": "Arabic",
        "items": ARABIC_ITEMS,
        "prompt_template": (
            'Please polish this Arabic note while keeping the answer in Arabic '
            'and not translating it into English: "{text}"'
        ),
        "repair_prompt_1": "Please keep the polished answer in Arabic.",
        "repair_prompt_2": "Do not translate into English. Output only the polished Arabic text.",
        "forbidden_markers": ["Here is", "Claro", "प्रिय", "नमस्ते"],
        "notes": "English instruction with Arabic target content.",
    },
    {
        "coverage_slice": "spanish_instruction_arabic_quote",
        "id_prefix": "v03_es_ar_EP",
        "language_pair": "es-ar",
        "instruction_language": "Spanish",
        "content_language": "Arabic",
        "expected_response_language": "Arabic",
        "expected_script": "Arabic",
        "items": ARABIC_ITEMS,
        "prompt_template": '¿Puedes mejorar esta cita en árabe sin traducirla al español ni cambiar sus términos clave? "{text}"',
        "repair_prompt_1": "Mantén la respuesta en árabe y no traduzcas la cita al español.",
        "repair_prompt_2": "Responde solo con la versión árabe pulida.",
        "forbidden_markers": ["Claro", "Aquí tienes", "El ", "La ", "Here is", "प्रिय", "नमस्ते"],
        "notes": "Spanish instruction with Arabic target content; targets non-English-to-non-English preservation.",
    },
    {
        "coverage_slice": "hindi_english_instruction_hindi_devanagari",
        "id_prefix": "v03_hi_hi_EP",
        "language_pair": "hi-hi",
        "instruction_language": "Hindi/English code-switched",
        "content_language": "Hindi",
        "expected_response_language": "Hindi",
        "expected_script": "Devanagari",
        "items": HINDI_ITEMS,
        "prompt_template": (
            'Is Hindi note ko natural bana do, lekin Devanagari Hindi hi rakho '
            'aur English translation mat banao: "{text}"'
        ),
        "repair_prompt_1": "Hindi Devanagari mein hi jawab do; English mein translate mat karo.",
        "repair_prompt_2": "Sirf sudhara hua Hindi text do.",
        "forbidden_markers": ["Here is", "Claro", "بالطبع", "إليك"],
        "notes": "Hindi-English code-switched instruction with Hindi Devanagari target content.",
    },
    {
        "coverage_slice": "arabic_instruction_arabic_filenames",
        "id_prefix": "v03_ar_ar_EP",
        "language_pair": "ar-ar",
        "instruction_language": "Arabic",
        "content_language": "Arabic with English file names",
        "expected_response_language": "Arabic",
        "expected_script": "Arabic",
        "items": ARABIC_FILENAME_ITEMS,
        "prompt_template": 'يرجى تحسين هذه الرسالة بالعربية مع إبقاء أسماء الملفات بالإنجليزية كما هي: "{text}"',
        "repair_prompt_1": "أبق الرد بالعربية، ولا تغير أسماء الملفات الإنجليزية.",
        "repair_prompt_2": "اكتب النسخة العربية المحسنة فقط مع حفظ أسماء الملفات كما هي.",
        "forbidden_markers": ["Here is", "Claro", "budget plan", "presentation draft", "प्रिय", "नमस्ते"],
        "notes": "Arabic instruction and Arabic target content with literal English file-name preservation.",
    },
]


def make_row(spec: dict[str, Any], index: int, text: str, spans: list[str]) -> dict[str, Any]:
    return {
        "id": f"{spec['id_prefix']}_{index:03d}",
        "benchmark_version": VERSION,
        "validation_status": VALIDATION_STATUS,
        "coverage_slice": spec["coverage_slice"],
        "language_pair": spec["language_pair"],
        "task_family": "editing_preservation",
        "user_prompt": spec["prompt_template"].format(text=text),
        "instruction_language": spec["instruction_language"],
        "content_language": spec["content_language"],
        "expected_response_language": spec["expected_response_language"],
        "expected_script": spec["expected_script"],
        "must_preserve_spans": spans,
        "register_requirement": "natural edited message in the target content language",
        "locale_requirement": None,
        "acceptable_outputs": [
            "satisfies the expected target language, script, preservation, register, and task constraints",
        ],
        "known_bad_outputs": [
            "translation into the instruction language",
            "English paraphrase of the target-language content",
            "omission or translation of preserved target-language terms",
        ],
        "repair_prompt_1": spec["repair_prompt_1"],
        "repair_prompt_2": spec["repair_prompt_2"],
        "required_any_markers": spans,
        "forbidden_markers": spec["forbidden_markers"],
        "notes_for_annotators": (
            f"{spec['notes']} Synthetic scaffold only; requires native validation before claims."
        ),
        "stress_tag": "non_english_target_content_preservation",
    }


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in SLICE_SPECS:
        for index, (text, spans) in enumerate(spec["items"], start=1):
            rows.append(make_row(spec, index, text, spans))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    rows = build_rows()
    write_jsonl(args.out, rows)
    print(f"wrote {len(rows)} synthetic v0.3 expansion rows to {args.out}")


if __name__ == "__main__":
    main()
