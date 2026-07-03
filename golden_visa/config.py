"""Load case-specific configuration from YAML."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ApplicantConfig:
    slug: str


@dataclass
class EmploymentContractConfig:
    first_page: int
    salary_page: int
    signature_page: int


@dataclass
class BankStatementsConfig:
    directory: Path
    employer_salary_patterns: list[str]
    account_pattern: str
    usd_aed_rate: float
    default_salary_usd: float
    missing_salary_month: str
    missing_salary_explanation: str


@dataclass
class WorkPermitConfig:
    rotations: tuple[int, int]


@dataclass
class DocumentMapping:
    source: Path
    output: str
    stack_pages: bool = False


@dataclass
class CaseConfig:
    root: Path
    applicant: ApplicantConfig
    sources: Path
    ready: Path
    bank_statements: BankStatementsConfig
    employment_contract: EmploymentContractConfig | None
    employment_contract_file: Path | None
    work_permit: WorkPermitConfig
    residence_visa: Path
    emirates_id: Path
    work_permit_file: Path
    passport: Path | None
    photo: Path | None
    photo_output: str
    passport_output: str
    residence_visa_output: str
    emirates_id_output: str
    work_permit_output: str
    single_documents: list[DocumentMapping] = field(default_factory=list)
    ocr_tmp: Path = field(default_factory=lambda: ROOT / ".cache" / "ocr_tmp.png")

    def resolve(self, relative: str | Path) -> Path:
        path = Path(relative)
        if path.is_absolute():
            return path
        return self.root / path


def _require(data: dict[str, Any], key: str) -> Any:
    if key not in data:
        raise ValueError(f"Missing required config key: {key}")
    return data[key]


def load_config(path: Path | None = None) -> CaseConfig:
    config_path = path or ROOT / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(
            f"No config at {config_path}. Copy config.example.yaml to config.yaml and edit it."
        )

    with config_path.open() as handle:
        raw = yaml.safe_load(handle)

    root = ROOT
    sources = root / _require(raw, "sources_dir")
    ready = root / raw.get("ready_dir", "ready")

    bank_raw = _require(raw, "bank_statements")
    bank = BankStatementsConfig(
        directory=root / _require(bank_raw, "directory"),
        employer_salary_patterns=list(_require(bank_raw, "employer_salary_patterns")),
        account_pattern=_require(bank_raw, "account_pattern"),
        usd_aed_rate=float(bank_raw.get("usd_aed_rate", 3.6725)),
        default_salary_usd=float(bank_raw.get("default_salary_usd", 10_000.0)),
        missing_salary_month=str(bank_raw.get("missing_salary_month", "")).lower(),
        missing_salary_explanation=str(bank_raw.get("missing_salary_explanation", "")).strip(),
    )

    employment: EmploymentContractConfig | None = None
    employment_file: Path | None = None
    if "employment_contract" in raw:
        contract_raw = raw["employment_contract"]
        employment = EmploymentContractConfig(
            first_page=int(_require(contract_raw, "first_page")),
            salary_page=int(_require(contract_raw, "salary_page")),
            signature_page=int(_require(contract_raw, "signature_page")),
        )
        if "source" in contract_raw:
            employment_file = root / contract_raw["source"]

    work_raw = raw.get("work_permit", {})
    work_permit = WorkPermitConfig(
        rotations=tuple(work_raw.get("rotations", [270, 90])),
    )

    identity = _require(raw, "identity_documents")
    applicant_raw = _require(raw, "applicant")

    single_documents: list[DocumentMapping] = []
    for item in raw.get("single_documents", []):
        single_documents.append(
            DocumentMapping(
                source=root / _require(item, "source"),
                output=_require(item, "output"),
                stack_pages=bool(item.get("stack_pages", False)),
            )
        )

    passport_path = raw.get("passport")
    photo_path = raw.get("photo")

    return CaseConfig(
        root=root,
        applicant=ApplicantConfig(slug=_require(applicant_raw, "slug")),
        sources=sources,
        ready=ready,
        bank_statements=bank,
        employment_contract=employment,
        employment_contract_file=employment_file,
        work_permit=work_permit,
        residence_visa=root / _require(identity, "residence_visa"),
        emirates_id=root / _require(identity, "emirates_id"),
        work_permit_file=root / _require(identity, "work_permit"),
        passport=root / passport_path if passport_path else None,
        photo=root / photo_path if photo_path else None,
        photo_output=raw.get("photo_output", "passport-photo-{slug}.jpg"),
        passport_output=raw.get("passport_output", "passport-front-and-back.pdf"),
        residence_visa_output=identity.get("residence_visa_output", "residence-visa.pdf"),
        emirates_id_output=identity.get("emirates_id_output", "emirates-id-front-and-back.pdf"),
        work_permit_output=identity.get("work_permit_output", "work-permit-front-and-back.pdf"),
        single_documents=single_documents,
    )
