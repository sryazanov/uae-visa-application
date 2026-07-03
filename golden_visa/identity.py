"""Residence visa, Emirates ID, and work permit layout."""

from __future__ import annotations

import fitz

from golden_visa.config import CaseConfig
from golden_visa.pdf import card_row_dimensions, compress_pdf, page_content_rect


def prepare_residence_visa(config: CaseConfig) -> None:
    doc = fitz.open(config.residence_visa)
    compress_pdf(doc, config.ready / config.residence_visa_output)
    doc.close()


def prepare_emirates_id(config: CaseConfig) -> None:
    eid_doc = fitz.open(config.emirates_id)
    target_w = 920.0
    padding = 20.0
    gap = 12.0
    _, eid_w, eid_h = card_row_dimensions(eid_doc[0], target_w, gap)
    eid_scale = eid_w / eid_doc[0].rect.width

    page_w = target_w + 2 * padding
    page_h = eid_h + 2 * padding

    merged = fitz.open()
    page = merged.new_page(width=page_w, height=page_h)
    x = padding
    for i in range(min(2, len(eid_doc))):
        page.show_pdf_page(
            fitz.Rect(x, padding, x + eid_w, padding + eid_h),
            eid_doc,
            i,
        )
        x += eid_w + gap * eid_scale

    compress_pdf(merged, config.ready / config.emirates_id_output)
    merged.close()
    eid_doc.close()


def prepare_work_permit(config: CaseConfig) -> None:
    emp_doc = fitz.open(config.work_permit_file)
    eid_doc = fitz.open(config.emirates_id)

    target_w = 920.0
    padding = 20.0
    gap = 12.0
    _, slot_w, slot_h = card_row_dimensions(eid_doc[0], target_w, gap)
    slot_scale = slot_w / eid_doc[0].rect.width
    eid_doc.close()

    rotations = config.work_permit.rotations
    emp_clips = [page_content_rect(emp_doc[i]) for i in range(min(2, len(emp_doc)))]

    page_w = target_w + 2 * padding
    page_h = slot_h + 2 * padding

    merged = fitz.open()
    page = merged.new_page(width=page_w, height=page_h)
    x = padding
    for i, clip in enumerate(emp_clips):
        page.show_pdf_page(
            fitz.Rect(x, padding, x + slot_w, padding + slot_h),
            emp_doc,
            i,
            clip=clip,
            rotate=rotations[i] if i < len(rotations) else 0,
            keep_proportion=True,
        )
        x += slot_w + gap * slot_scale

    compress_pdf(merged, config.ready / config.work_permit_output)
    merged.close()
    emp_doc.close()


def prepare_identity_documents(config: CaseConfig) -> None:
    prepare_residence_visa(config)
    prepare_emirates_id(config)
    prepare_work_permit(config)
