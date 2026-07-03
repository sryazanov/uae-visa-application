# Lessons learned — Golden Visa applications

Practical lessons from successful GDRFA portal applications. Use alongside [PRINCIPLES.md](PRINCIPLES.md) (rules) and [WORKFLOW.md](WORKFLOW.md) (process).

An AI agent plus this harness turns a vague, manual upload process into a structured, verifiable submission.

---

## 1. Navigating officer remarks

Officers often use **standardised boilerplate** in Arabic. The text sounds specific but usually maps to a simple checklist item.

### Find the real requirement

| Remark (translated) | What the officer usually wants |
|---------------------|--------------------------------|
| Employment contract from DWTCA | Proof that your employer is licensed under Dubai World Trade Centre Authority |
| 6 months bank statements with salary | Salary credits visible on the right pages, easy to verify |
| Passport | Clear, readable bio page |

Do not take vague wording literally. Ask: *what box on their checklist am I failing?*

### The linkage strategy

When the officer asks for an **authority-branded contract** (e.g. “DWTCA employment contract”) and your company cannot produce one:

1. Upload the **employment contract** you have (first, salary, signature pages separately).
2. Add the company **trade licence** — it carries the official government stamp and proves jurisdiction.
3. Add a **clarification letter** (English) that explicitly links the documents: company name on licence matches employer on contract and bank statements.

This bridges the gap between what the portal asks for and what employers actually issue.

---

## 2. Technical upload efficiency

### How the portal handles uploads

Observed GDRFA portal behaviour:

- **Upload slots are added over time.** On first submission you may not have enough slots for every document. Additional upload fields often appear after the officer requests more documents. Do not assume the initial form is the final list — plan to resubmit with extra slots.
- **Files are converted to JPEG.** The portal rasterises uploads. Fine text and small details can lose clarity — keep annotations large and high-contrast (the pipeline’s salary notes and EXPLANATION boxes are designed for this).
- **Only the first PDF page is kept.** Multi-page PDFs are silently truncated: page 1 becomes a JPEG; pages 2+ are discarded. This is the main reason the harness outputs single-page files.

### Avoid truncation

Because of the first-page-only rule:

- **One page per PDF** — always, for every document type
- **One subject per file** — unbundle visa, Emirates ID, work permit, and each contract page
- **Under 1 MB** — large files may compress poorly after JPEG conversion (the pipeline compresses automatically)

If you ever bundled before learning this rule, assume the officer only saw page 1. Re-upload each page as its own file.

### File naming

Use **self-descriptive, sequential names** so the officer can follow your submission without opening every file:

```
01_Statement_Jan2026.pdf
02_Statement_Feb2026.pdf
employment-contract-salary-page.pdf
trade-licence.pdf
salary-and-employment-clarification-letter.pdf
```

When resubmitting after remarks, reference these names in your cover letter by number.

---

## 3. Salary and currency

### Currency conversion

If salary is paid in **USD** but the requirement is stated in **AED**:

- Add a visible note on each bank statement next to the salary credit
- Use a **fixed exchange rate** (e.g. 1 USD = 3.6725 AED) and show the calculation
- Do the math for the officer — do not make them convert manually

The pipeline adds these notes automatically when configured in `config.yaml`.

### Payroll timing

Salary may appear in the “wrong” statement month when pay day falls on a weekend or holiday, or when two payments land in one period.

- Proactively add an **EXPLANATION** box on affected statements
- Describe your pay schedule plainly (e.g. “official pay date is the 25th”)
- Confirm all required payments are present across the full set of statements

---

## 4. The clarification / cover letter

Treat the clarification letter as a **map for the reviewer**, not just a formality.

- Place it **first** in the upload set when resubmitting after remarks
- State what you are applying for and what changed since the last submission
- **Number your files** and point to specific documents:

  > “Please see `trade-licence.pdf` for DWTCA jurisdiction and `employment-contract-first-page.pdf` for employer details.”

- Keep tone professional, polite, and factual

The agent can draft this letter in English; you review before adding to `sources/`.

---

## 5. Managing portal status

### Locked files

Files that are **locked** or have **no Delete button** have been accepted by the system for that review stage. They are waiting on further processing — not rejected.

- Do **not** waste effort re-uploading locked documents
- Focus corrections only on **flagged or editable** slots
- Track what is locked vs open in `OFFICER_REMARKS.txt` resolution notes

### Remark rounds

Officers may narrow their request in a second round (e.g. first remark asks for three items; second remark asks only for the contract). That usually means other items were accepted.

---

## How this harness applies each lesson

| Lesson | Harness support |
|--------|-----------------|
| Remark translation | `OFFICER_REMARKS.txt` + agent (`AGENTS.md`) |
| Unbundling / compression | `prepare.py` → single-page `ready/` files (portal keeps page 1 only) |
| Salary highlights + AED notes | `golden_visa/bank_statements.py` + `config.yaml` |
| Missing-salary explanation | `missing_salary_explanation` in `config.yaml` |
| Clarification letter | `sources/salary-clarification-letter.pdf` → `ready/` |
| Trade licence + contract linkage | `single_documents` in `config.yaml` |
| Sequential statement names | `01_Statement_…` output naming |

---

## For agents

When diagnosing a remark, read [PRINCIPLES.md](PRINCIPLES.md) and this file, then:

1. Translate the remark in `OFFICER_REMARKS.txt`
2. Identify the checklist item (use the table in §1)
3. Apply the linkage strategy if the remark is about authority/jurisdiction
4. Propose the smallest change to `config.yaml` or `sources/`
5. Regenerate and draft cover-letter language that maps file names to requirements
