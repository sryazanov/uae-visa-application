# Document checklist

Use this checklist when gathering `sources/` and reviewing `ready/` before upload.

**Portal:** apply and upload documents at [GDRFA Dubai Smart Services](https://smart.gdrfad.gov.ae/en/) (login with UAE Pass or registered account).  
**Service info:** [Golden Residency services](https://www.gdrfad.gov.ae/en/services/335969f4-8045-11ed-4fe5-0050569629e8) on the GDRFA website.  
**Skilled-worker category** (salary ≥ AED 30,000): see [official requirements](https://gdrfad.gov.ae/en/services/8ea80daa-f43e-11eb-0320-0050569629e8) — passport, employment contract or salary certificate, 6 months of salary bank statements, degree certificate, and professional licence if applicable.

> Requirements vary by Golden Visa category and may change. The portal may show **fewer upload slots initially** and add more after officer remarks. See [LEARNINGS.md](LEARNINGS.md) §2.

---

## Before you upload

- [ ] Every `ready/` PDF is **single-page** (portal keeps page 1 only, converts to JPEG)
- [ ] Every file is **under 1 MB**
- [ ] Bank statements show **highlighted salary** and USD→AED notes if paid in foreign currency
- [ ] Clarification letter uploaded **first** when resubmitting after remarks
- [ ] Filenames are self-descriptive (officer sees JPEGs, not your folder structure)

---

## Document checklist

| # | Document | Required for | Source (`sources/`) | Output (`ready/`) | Pipeline |
|---|----------|--------------|---------------------|-------------------|----------|
| 1 | Passport (bio page) | All categories | `passport.pdf` | `passport-front-and-back.pdf` | Yes |
| 2 | Passport photo | All categories | `passport-photo.jpg` | `passport-photo-{slug}.jpg` | Yes |
| 3 | Residence visa | In-country renewal / status | `residence-visa.pdf` | `residence-visa.pdf` | Yes |
| 4 | Emirates ID (front + back) | Identity verification | `emirates-id.pdf` | `emirates-id-front-and-back.pdf` | Yes |
| 5 | Work permit / employment card | Employment proof | `work-permit.pdf` | `work-permit-front-and-back.pdf` | Yes |
| 6 | Bank statements (6 months, salary page each) | Skilled worker | `bank-statements/*.pdf` | `01_Statement_…pdf` … | Yes |
| 7 | Employment contract — first page | Skilled worker | `employment-contract.pdf` | `employment-contract-first-page.pdf` | Yes |
| 8 | Employment contract — salary page | Skilled worker | ↑ | `employment-contract-salary-page.pdf` | Yes |
| 9 | Employment contract — signature page | Skilled worker | ↑ | `employment-contract-signature-page.pdf` | Yes |
| 10 | NOC for Golden Visa | Skilled worker; **free zone authority** (not the company) | `noc.pdf` | `noc-golden-visa.pdf` | Yes |
| 11 | Salary certificate | Skilled worker; **free zone authority** for FZ employers (not the company) | `salary-certificate.pdf` | `salary-certificate-golden-visa.pdf` | Yes |
| 12 | Certificate of recognition | Qualification proof; **Ministry of Education** | `certificate-of-recognition.pdf` | `certificate-of-recognition.pdf` | Yes |
| 13 | Salary & employment clarification letter | Remarks / jurisdiction | `salary-clarification-letter.pdf` | `salary-and-employment-clarification-letter.pdf` | Yes |
| 14 | Company trade licence | **Links contract ↔ free-zone certificates**; proves jurisdiction (e.g. DWTCA) | `trade-licence.pdf` | `trade-licence.pdf` | Yes |
| 15 | Degree certificate + attestation | Skilled worker (official) | *add to `sources/`* | *manual* | No |
| 16 | Professional licence | If profession requires it | *add to `sources/`* | *manual* | No |

---

## Issuing authority (observed)

Requirements vary by category and employer type. In practice for **free zone** employers:

- **Salary certificate** — obtain from the **free zone authority** (e.g. DWTCA), not a company HR letter. Often issued in Arabic.
- **NOC for Golden Visa** — when required, also from the **free zone authority**, not the company.
- **Company trade licence** — important linkage document. The employment contract names the company; the salary certificate and NOC come from the free zone authority. The **trade licence** (issued by that authority) proves the company operates under it and ties the set together. Pair with the clarification letter when officers ask for an “authority-branded” contract — see [LEARNINGS.md](LEARNINGS.md) §1.

For **qualification** documents:

- **Certificate of recognition** — issued by the **Ministry of Education** (UAE), not the employer.

---

## Bank statements detail

For each of the **6 required salary months**, the pipeline produces one file:

| Output pattern | Meaning |
|----------------|---------|
| `01_Statement_Jan2026.pdf` | Salary credit found on this statement |
| `03_Statement_NA_Feb2026.pdf` | No salary on this period — includes EXPLANATION box |

Place raw statement PDFs in `sources/bank-statements/`. Configure OCR patterns and explanation text in `config.yaml`.

---

## Documents often requested via remarks

If the officer's remark mentions these, see [LEARNINGS.md](LEARNINGS.md) §1:

| Remark theme | Likely fix |
|--------------|------------|
| DWTCA / free-zone employment contract | Trade licence + clarification letter + contract pages |
| 6 months salary not visible | Re-check statement page selection and highlights |
| Passport unclear | Re-scan or re-upload `passport-front-and-back.pdf` |

Track remarks in `OFFICER_REMARKS.txt` (gitignored).

---

## Quick source folder layout

```
sources/
├── passport.pdf
├── passport-photo.jpg
├── residence-visa.pdf
├── emirates-id.pdf
├── work-permit.pdf
├── employment-contract.pdf
├── bank-statements/
│   └── *.pdf
├── noc.pdf
├── salary-certificate.pdf
├── certificate-of-recognition.pdf
├── trade-licence.pdf
└── salary-clarification-letter.pdf
```

Run `python prepare.py` → review all files in `ready/` against this checklist → upload at [smart.gdrfad.gov.ae](https://smart.gdrfad.gov.ae/en/).
