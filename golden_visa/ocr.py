"""OCR helpers (requires Tesseract installed locally)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import fitz


def ocr_text(page: fitz.Page, ocr_tmp: Path, scale: float = 3.0) -> str:
    ocr_tmp.parent.mkdir(parents=True, exist_ok=True)
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    pix.save(str(ocr_tmp))
    result = subprocess.run(
        ["tesseract", str(ocr_tmp), "stdout", "-l", "eng", "--psm", "6"],
        capture_output=True,
    )
    return result.stdout.decode("utf-8", errors="replace")


def ocr_word_boxes(page: fitz.Page, ocr_tmp: Path, scale: float = 3.0) -> list[tuple[str, fitz.Rect]]:
    ocr_tmp.parent.mkdir(parents=True, exist_ok=True)
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    pix.save(str(ocr_tmp))
    tsv = subprocess.run(
        ["tesseract", str(ocr_tmp), "stdout", "-l", "eng", "--psm", "6", "tsv"],
        capture_output=True,
    ).stdout.decode("utf-8", errors="replace")
    boxes: list[tuple[str, fitz.Rect]] = []
    page_rect = page.rect
    img_w, img_h = pix.width, pix.height
    sx = page_rect.width / img_w
    sy = page_rect.height / img_h
    for line in tsv.splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) < 12:
            continue
        text = parts[11].strip()
        if not text:
            continue
        left, top, width, height = map(int, parts[6:10])
        rect = fitz.Rect(left * sx, top * sy, (left + width) * sx, (top + height) * sy)
        boxes.append((text, rect))
    return boxes
