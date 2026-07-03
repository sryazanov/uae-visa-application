"""Orchestrate document preparation from case configuration."""

from __future__ import annotations

from golden_visa.bank_statements import prepare_bank_statements
from golden_visa.config import CaseConfig
from golden_visa.documents import prepare_passport, prepare_photo, prepare_single_documents
from golden_visa.employment import prepare_employment_contract
from golden_visa.identity import prepare_identity_documents


def reset_ready_dir(config: CaseConfig) -> None:
    if config.ready.exists():
        for item in config.ready.iterdir():
            item.unlink()
    else:
        config.ready.mkdir(parents=True)


def run_pipeline(config: CaseConfig) -> list[tuple[str, float]]:
    reset_ready_dir(config)
    prepare_bank_statements(config)
    prepare_employment_contract(config)
    prepare_identity_documents(config)
    prepare_single_documents(config)
    prepare_passport(config)
    prepare_photo(config)

    if config.ocr_tmp.exists():
        config.ocr_tmp.unlink()

    return [
        (path.name, path.stat().st_size / 1024)
        for path in sorted(config.ready.iterdir())
    ]
