"""Bank statement preparation: salary page selection, highlights, and notes."""

from __future__ import annotations

import html
import re
from pathlib import Path

import fitz

from golden_visa.config import CaseConfig
from golden_visa.ocr import ocr_text, ocr_word_boxes
from golden_visa.pdf import save_pdf_single_page

CM_TO_PT = 72 / 2.54

MONTH_NUM_TO_NAME = {
    "01": "january",
    "02": "february",
    "03": "march",
    "04": "april",
    "05": "may",
    "06": "june",
    "07": "july",
    "08": "august",
    "09": "september",
    "10": "october",
    "11": "november",
    "12": "december",
}

MONTH_ABBR_TO_NUM = {
    "JAN": "01",
    "FEB": "02",
    "MAR": "03",
    "APR": "04",
    "MAY": "05",
    "JUN": "06",
    "JUL": "07",
    "AUG": "08",
    "SEP": "09",
    "OCT": "10",
    "NOV": "11",
    "DEC": "12",
}

MONTH_NUM_TO_ABBR = {
    "01": "Jan",
    "02": "Feb",
    "03": "Mar",
    "04": "Apr",
    "05": "May",
    "06": "Jun",
    "07": "Jul",
    "08": "Aug",
    "09": "Sep",
    "10": "Oct",
    "11": "Nov",
    "12": "Dec",
}

NAME_TO_NUM = {name: num for num, name in MONTH_NUM_TO_NAME.items()}


def score_salary_page(text: str, employer_patterns: list[str], account_pattern: str) -> int:
    tl = text.lower()
    score = 0
    for pattern in employer_patterns:
        if pattern.lower() in tl:
            score += 100
    if "salary payment" in tl:
        score += 90
    if "salary back pay" in tl:
        score += 85
    if "/uri/" in tl and "salary" in tl:
        score += 80
    if "directors salary" in tl and re.search(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b", text):
        score += 60
    if "directors salary" in tl:
        score -= 20
    if account_pattern in text and "salary" in tl:
        score += 10
    return score


def pick_salary_page(
    doc: fitz.Document,
    config: CaseConfig,
) -> tuple[int, bool]:
    bank = config.bank_statements
    best_idx = 0
    best_score = -999
    for idx, page in enumerate(doc):
        score = score_salary_page(ocr_text(page, config.ocr_tmp), bank.employer_salary_patterns, bank.account_pattern)
        if score > best_score:
            best_score = score
            best_idx = idx
    has_salary = best_score > 0
    if has_salary:
        return best_idx, True

    for idx, page in enumerate(doc):
        text = ocr_text(page, config.ocr_tmp)
        tl = text.lower()
        if bank.account_pattern in text and "transaction details" in tl:
            return idx, False

    return best_idx, False


def extract_salary_deposits(text: str) -> list[float]:
    lines = text.split("\n")
    amount_re = re.compile(r"\b(\d{1,3}(?:,\d{3})*\.\d{2})\b")
    deposits: list[float] = []
    for i, line in enumerate(lines):
        if "salary" not in line.lower():
            continue
        window = "\n".join(lines[i : i + 8])
        amounts = [float(m.replace(",", "")) for m in amount_re.findall(window)]
        candidates = [amount for amount in amounts if 5_000 <= amount <= 50_000]
        if candidates:
            deposits.append(candidates[0])
    return deposits


def format_salary_note(usd_amount: float, usd_aed_rate: float) -> str:
    usd_rounded = int(round(usd_amount))
    aed_rounded = int(round(usd_amount * usd_aed_rate))
    return (
        f"Monthly Salary: ${usd_rounded:,} USD "
        f"(equivalent to AED {aed_rounded:,}+ at {usd_aed_rate} rate)"
    )


def merge_overlapping_rects(rects: list[fitz.Rect]) -> list[fitz.Rect]:
    unique: list[fitz.Rect] = []
    for rect in rects:
        duplicate = False
        for existing in unique:
            intersection = rect & existing
            if intersection.is_empty:
                continue
            min_area = min(rect.get_area(), existing.get_area())
            if min_area and intersection.get_area() / min_area > 0.5:
                duplicate = True
                break
        if not duplicate:
            unique.append(rect)
    return sorted(unique, key=lambda r: (r.y0, r.x0))


def add_explanation_box(page: fitz.Page, rect: fitz.Rect, text: str) -> None:
    body = html.escape(text).replace("\n", "<br>")
    html_content = (
        '<div style="border:2.5px solid #a60000;background:#ffffff;padding:14px 16px;'
        'color:#cc0000;font-family:Helvetica,sans-serif;font-size:14pt;line-height:1.45;">'
        '<b style="font-size:18pt;display:block;margin-bottom:10px;">EXPLANATION</b>'
        f"{body}</div>"
    )
    page.insert_htmlbox(rect, html_content)


def add_salary_amount_note(
    page: fitz.Page,
    anchor: fitz.Rect,
    usd_amount: float,
    usd_aed_rate: float,
    note_index: int = 0,
) -> None:
    note = format_salary_note(usd_amount, usd_aed_rate)
    note_w = min(360, page.rect.width - 16)
    note_h = 40
    left = max(8, min(anchor.x0, page.rect.width - note_w - 8))
    top = min(anchor.y1 + 4 + note_index * (note_h + 2), page.rect.height - note_h - 6)
    rect = fitz.Rect(left, top, left + note_w, top + note_h)
    shape = page.new_shape()
    shape.draw_rect(rect)
    shape.finish(color=(0.65, 0.0, 0.0), fill=(0.85, 0.85, 0.85), fill_opacity=1.0, width=1.5)
    shape.commit()
    html_content = (
        '<div style="background:#d9d9d9;padding:5px 7px;'
        'color:#cc0000;font-family:Helvetica,sans-serif;font-size:10pt;font-weight:bold;'
        f'line-height:1.2;">{html.escape(note)}</div>'
    )
    page.insert_htmlbox(rect, html_content)


def highlight_salary(page: fitz.Page, config: CaseConfig) -> None:
    bank = config.bank_statements
    text = ocr_text(page, config.ocr_tmp)
    deposits = extract_salary_deposits(text)
    boxes = ocr_word_boxes(page, config.ocr_tmp)
    salary_rects: list[fitz.Rect] = []
    for i, (word, rect) in enumerate(boxes):
        if "salary" not in word.lower():
            continue
        merged = fitz.Rect(rect)
        for j in range(max(0, i - 8), min(len(boxes), i + 12)):
            merged |= boxes[j][1]
        salary_rects.append(merged)

    salary_rects = merge_overlapping_rects(salary_rects)
    if not salary_rects:
        return

    if not deposits:
        deposits = [bank.default_salary_usd]

    for idx, highlight in enumerate(salary_rects):
        padded = highlight + (-4, -4, 4, 4)
        shape = page.new_shape()
        shape.draw_rect(padded)
        shape.finish(color=(1, 0.9, 0.2), fill=(1, 1, 0), fill_opacity=0.12, width=0.75)
        shape.commit()
        amount = deposits[min(idx, len(deposits) - 1)]
        add_salary_amount_note(page, padded, amount, bank.usd_aed_rate, idx)


def add_missing_salary_explanation(page: fitz.Page, explanation: str) -> None:
    box_height = 210.0
    margin = 36.0
    bottom_y = page.rect.height - 5 * CM_TO_PT
    rect = fitz.Rect(margin, bottom_y - box_height, page.rect.width - margin, bottom_y)
    add_explanation_box(page, rect, explanation)


def statement_month_key(filename: str) -> str:
    match = re.match(r"(\d{2})\s+(\w+)\.pdf", filename, re.I)
    return match.group(2).lower() if match else ""


def parse_statement_date(text: str) -> tuple[int, str] | None:
    compact = re.sub(r"\s+", "", text.upper())
    match = re.search(r"STATEMENTDATE(\d{2})([A-Z]{3})(\d{4})", compact)
    if not match:
        match = re.search(r"(\d{2})([A-Z]{3})(\d{4})", compact)
    if not match:
        return None
    _, month_abbr, year = match.groups()
    month_num = MONTH_ABBR_TO_NUM.get(month_abbr)
    if not month_num:
        return None
    return int(year), MONTH_NUM_TO_NAME[month_num]


def parse_statement_sort_key(text: str) -> tuple[int, int] | None:
    parsed = parse_statement_date(text)
    if not parsed:
        return None
    year, month_name = parsed
    return year, int(NAME_TO_NUM[month_name])


def statement_period_label(text: str, fallback_filename: str) -> str:
    parsed = parse_statement_date(text)
    if parsed:
        year, month_name = parsed
        month_num = NAME_TO_NUM[month_name]
        return f"{MONTH_NUM_TO_ABBR[month_num]}{year}"
    month = statement_month_key(fallback_filename)
    if month:
        month_num = NAME_TO_NUM.get(month, "01")
        return MONTH_NUM_TO_ABBR[month_num]
    stem = Path(fallback_filename).stem.replace(" ", "")
    return stem


def statement_output_name(sequence: int, has_salary: bool, period_label: str) -> str:
    if has_salary:
        return f"{sequence:02d}_Statement_{period_label}.pdf"
    return f"{sequence:02d}_Statement_NA_{period_label}.pdf"


def prepare_bank_statements(config: CaseConfig) -> None:
    bank = config.bank_statements
    entries: list[dict] = []
    for src in sorted(bank.directory.glob("*.pdf")):
        doc = fitz.open(src)
        date_text = ocr_text(doc[0], config.ocr_tmp)
        page_idx, has_salary = pick_salary_page(doc, config)
        entries.append(
            {
                "doc": doc,
                "page_idx": page_idx,
                "has_salary": has_salary,
                "src": src,
                "date_text": date_text,
                "sort_key": parse_statement_sort_key(date_text) or (9999, 12),
                "period_label": statement_period_label(date_text, src.name),
                "month_key": statement_month_key(src.name),
            }
        )

    entries.sort(key=lambda item: item["sort_key"])

    for sequence, entry in enumerate(entries, start=1):
        doc = entry["doc"]
        page = doc[entry["page_idx"]]
        if entry["has_salary"]:
            highlight_salary(page, config)
        elif (
            bank.missing_salary_month
            and entry["month_key"] == bank.missing_salary_month
            and bank.missing_salary_explanation
        ):
            add_missing_salary_explanation(page, bank.missing_salary_explanation)
        out_name = statement_output_name(sequence, entry["has_salary"], entry["period_label"])
        save_pdf_single_page(page, config.ready / out_name)
        doc.close()
