"""Employment contract page extraction."""

from __future__ import annotations

import fitz

from golden_visa.config import CaseConfig
from golden_visa.pdf import save_pdf_page_from_doc


def prepare_employment_contract(config: CaseConfig) -> None:
    contract = config.employment_contract
    src = config.employment_contract_file
    if contract is None or src is None or not src.exists():
        return

    doc = fitz.open(src)
    pages = {
        "employment-contract-first-page.pdf": contract.first_page,
        "employment-contract-salary-page.pdf": contract.salary_page,
        "employment-contract-signature-page.pdf": contract.signature_page,
    }
    for out_name, page_idx in pages.items():
        if page_idx < len(doc):
            save_pdf_page_from_doc(doc, page_idx, config.ready / out_name)
    doc.close()
