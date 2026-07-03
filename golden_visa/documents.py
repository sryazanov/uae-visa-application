"""Passport, photo, and other single-document preparation."""

from __future__ import annotations

import fitz

from golden_visa.config import CaseConfig
from golden_visa.pdf import compress_image, compress_pdf, merge_pages_stacked


def prepare_single_documents(config: CaseConfig) -> None:
    for mapping in config.single_documents:
        if not mapping.source.exists():
            continue
        doc = fitz.open(mapping.source)
        if mapping.stack_pages and len(doc) > 1:
            merge_pages_stacked(list(doc), config.ready / mapping.output)
        else:
            compress_pdf(doc, config.ready / mapping.output)
        doc.close()


def prepare_passport(config: CaseConfig) -> None:
    if config.passport is None or not config.passport.exists():
        return
    doc = fitz.open(config.passport)
    if len(doc) > 1:
        merge_pages_stacked(list(doc), config.ready / config.passport_output)
    else:
        compress_pdf(doc, config.ready / config.passport_output)
    doc.close()


def prepare_photo(config: CaseConfig) -> None:
    if config.photo is None or not config.photo.exists():
        return
    out_name = config.photo_output.format(slug=config.applicant.slug)
    compress_image(config.photo, config.ready / out_name)
