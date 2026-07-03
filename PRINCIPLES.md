# Golden Visa document principles

These rules apply to **every** GDRFA portal upload, regardless of applicant. The pipeline encodes them; human review still required before submission.

## Portal technical constraints

| Rule | Why |
|------|-----|
| **Each file &lt; 1 MB** | Large files are rejected or compress poorly after portal JPEG conversion |
| **Single-page PDFs only** | Portal keeps **page 1 only**; remaining pages are silently discarded |
| **Unbundle everything** | Visa, Emirates ID, work permit, and each contract page = separate files |
| **Self-descriptive names** | Officers review dozens of applications; names are your index |
| **Sequential prefixes for sets** | e.g. `01_…`, `02_…` for bank statements guides chronological review |
| **Expect more upload slots later** | Initial submission may not have a slot per document; more appear after remarks |

## Document-specific rules

### Bank statements

- Upload **only the page showing salary credit** (not the full statement).
- **Highlight** salary line(s) in yellow.
- If salary is paid in **USD**, add a visible note with **USD → AED conversion** using a fixed rate (document the rate in the note, e.g. 3.6725).
- If a statement period has **no salary** due to payroll timing (weekends, holidays, early transfer), add an **EXPLANATION** box on that page — proactively, before the officer asks.
- Name files with statement period: `01_Statement_Dec2025.pdf` (use `Statement_NA` when salary is absent).

### Identity documents

- **Emirates ID**: front and back on **one page**, side by side.
- **Residence visa**: single page (do not bundle with EID unless portal requires it).
- **Work permit / employment card**: front and back on **one page**; crop letter-size scans to card content; rotate if scanned sideways.

### Employment contract

- Extract **three separate pages**: first page (parties/jurisdiction), salary terms, signature page.
- Page indices are **0-based** and vary by contract template — set in `config.yaml`.

### Passport and photo

- Passport: bio page (+ back if required) on one page when possible.
- Photo: JPEG under size limit.

### Supporting letters

- **Clarification / cover letter** should be the **first file** when resubmitting after remarks.
- Use the letter as a **map**: number your uploads and point to specific filenames (e.g. trade licence proving DWTCA jurisdiction).
- See [LEARNINGS.md](LEARNINGS.md) §4 for structure and tone.

## Handling officer remarks

Remarks on the GDRFA portal are usually in **Arabic**. Paste them verbatim into `OFFICER_REMARKS.txt`; use an AI agent to **translate and summarise** each remark in English (`# Summary`).

1. **Find the checklist item** — boilerplate text often hides a simple requirement (see [LEARNINGS.md](LEARNINGS.md) §1).
2. **Linkage strategy** — when an authority-branded contract is requested, combine employment contract + trade licence + clarification letter.
3. **Do not re-upload locked files** — no Delete button means accepted; fix only flagged/editable slots ([LEARNINGS.md](LEARNINGS.md) §5).
4. **Transparency over ambiguity** — explain currency, timing, and jurisdiction in clear English on the documents themselves.

## Naming conventions

```
# Bank statements (chronological)
01_Statement_Dec2025.pdf
03_Statement_NA_Feb2026.pdf   # no salary — includes explanation

# Identity (descriptive kebab-case)
residence-visa.pdf
emirates-id-front-and-back.pdf
work-permit-front-and-back.pdf

# Contract
employment-contract-first-page.pdf
employment-contract-salary-page.pdf
employment-contract-signature-page.pdf
```

## What belongs in config (case-specific)

Keep in `config.yaml` (gitignored), not in code:

- Source file paths
- Employment contract page numbers
- Employer name / salary OCR patterns
- Bank account number fragment for fallback page detection
- USD/AED rate and default salary amount
- Missing-salary explanation text (payroll schedule)
- Work permit rotation angles
- Output filename overrides

## What belongs in code (generic)

- PDF compression and layout
- OCR-based salary page detection (driven by config patterns)
- Highlight and annotation rendering
- Merge/crop/rotate utilities

When a new pattern benefits everyone (e.g. a different bank’s statement layout), generalise the **algorithm** and add the **values** to `config.example.yaml`.
