"""Generic PDF utilities for portal-ready documents."""

from __future__ import annotations

import io
from pathlib import Path

import fitz
from PIL import Image

MAX_BYTES = 1024 * 1024


def page_content_rect(page: fitz.Page, pad: float = 4.0) -> fitz.Rect:
    rects: list[fitz.Rect] = []
    for img in page.get_images(full=True):
        rects.extend(page.get_image_rects(img[0]))
    if not rects:
        return page.rect
    content = rects[0]
    for rect in rects[1:]:
        content |= rect
    return content + (-pad, -pad, pad, pad)


def card_row_dimensions(
    card_page: fitz.Page,
    target_w: float = 920.0,
    gap: float = 12.0,
) -> tuple[float, float, float]:
    scale = target_w / (card_page.rect.width * 2 + gap)
    card_w = card_page.rect.width * scale
    card_h = card_page.rect.height * scale
    return scale, card_w, card_h


def save_pdf_page_from_doc(doc: fitz.Document, page_idx: int, out_path: Path) -> None:
    out = fitz.open()
    out.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
    compress_pdf(out, out_path)
    out.close()


def save_pdf_single_page(page: fitz.Page, out_path: Path) -> None:
    doc = fitz.open()
    doc.insert_pdf(page.parent, from_page=page.number, to_page=page.number)
    compress_pdf(doc, out_path)
    doc.close()


def merge_pages_cropped_side_by_side(
    pages: list[fitz.Page],
    out_path: Path,
    gap: float = 16.0,
    padding: float = 20.0,
    target_content_width: float = 560.0,
) -> None:
    clips = [page_content_rect(p) for p in pages]
    card_w = max(c.width for c in clips)
    card_h = max(c.height for c in clips)
    scale = target_content_width / (len(pages) * card_w + gap * (len(pages) - 1))
    page_w = target_content_width + 2 * padding
    page_h = card_h * scale + 2 * padding

    merged = fitz.open()
    new_page = merged.new_page(width=page_w, height=page_h)
    x = padding
    for page, clip in zip(pages, clips):
        dest = fitz.Rect(x, padding, x + clip.width * scale, padding + clip.height * scale)
        new_page.show_pdf_page(dest, page.parent, page.number, clip=clip, keep_proportion=False)
        x += clip.width * scale + gap * scale

    compress_pdf(merged, out_path)
    merged.close()


def merge_pages_side_by_side(pages: list[fitz.Page], out_path: Path, gap: float = 12.0) -> None:
    widths = [p.rect.width for p in pages]
    heights = [p.rect.height for p in pages]
    total_w = sum(widths) + gap * (len(pages) - 1)
    total_h = max(heights)
    merged = fitz.open()
    new_page = merged.new_page(width=total_w, height=total_h)
    x = 0.0
    for page in pages:
        new_page.show_pdf_page(
            fitz.Rect(x, 0, x + page.rect.width, page.rect.height),
            page.parent,
            page.number,
        )
        x += page.rect.width + gap
    compress_pdf(merged, out_path)
    merged.close()


def merge_pages_stacked(pages: list[fitz.Page], out_path: Path, gap: float = 12.0) -> None:
    width = max(p.rect.width for p in pages)
    total_h = sum(p.rect.height for p in pages) + gap * (len(pages) - 1)
    merged = fitz.open()
    new_page = merged.new_page(width=width, height=total_h)
    y = 0.0
    for page in pages:
        new_page.show_pdf_page(
            fitz.Rect(0, y, page.rect.width, y + page.rect.height),
            page.parent,
            page.number,
        )
        y += page.rect.height + gap
    compress_pdf(merged, out_path)
    merged.close()


def compress_pdf(doc: fitz.Document, out_path: Path, max_bytes: int = MAX_BYTES) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = b""
    for quality in (85, 75, 65, 55, 45):
        buffer = io.BytesIO()
        doc.save(buffer, garbage=4, deflate=True, clean=True)
        data = buffer.getvalue()
        if len(data) <= max_bytes:
            out_path.write_bytes(data)
            return
        rendered = fitz.open()
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            img_buf = io.BytesIO()
            img.save(img_buf, format="JPEG", quality=quality, optimize=True)
            img_buf.seek(0)
            rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
            new_page = rendered.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(rect, stream=img_buf.read())
        buffer = io.BytesIO()
        rendered.save(buffer, garbage=4, deflate=True, clean=True)
        rendered.close()
        data = buffer.getvalue()
        if len(data) <= max_bytes:
            out_path.write_bytes(data)
            return
    out_path.write_bytes(data)


def compress_image(src: Path, out_path: Path, max_bytes: int = MAX_BYTES) -> None:
    img = Image.open(src)
    if img.mode != "RGB":
        img = img.convert("RGB")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    for quality in (90, 80, 70, 60, 50):
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        if buf.tell() <= max_bytes:
            out_path.write_bytes(buf.getvalue())
            return
    out_path.write_bytes(buf.getvalue())
