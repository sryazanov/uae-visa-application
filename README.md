# UAE Golden Visa — document preparation harness

A small **man-in-the-loop** toolkit for preparing GDRFA portal uploads: compress PDFs, extract the right pages, highlight salary, add explanatory notes, and name files so reviewers can follow your submission.

**Generic tooling is committed.** Your personal documents, config, and officer remarks stay local (gitignored). Committed example files use placeholders only — never real names, account numbers, or salaries.

## Quick start

```bash
# 1. Clone and install
pip install -r requirements.txt
# Tesseract OCR must be installed (macOS: brew install tesseract)

# 2. Configure your case
cp config.example.yaml config.yaml
cp OFFICER_REMARKS.example.txt OFFICER_REMARKS.txt
# Edit config.yaml — page indices, salary patterns, file paths
# Paste portal remarks into OFFICER_REMARKS.txt as they arrive

# 3. Add source documents
mkdir -p sources/bank-statements
# Place raw PDFs/JPGs under sources/ (see config.example.yaml for expected names)

# 4. Generate portal-ready files
python prepare.py
# Output appears in ready/
```

## Repository layout

| Path | Committed? | Purpose |
|------|------------|---------|
| `golden_visa/` | Yes | Generic PDF/OCR pipeline |
| `prepare.py` | Yes | Entry point |
| `config.example.yaml` | Yes | Documented template for new cases |
| `config.yaml` | **No** | Your case-specific settings |
| `OFFICER_REMARKS.txt` | **No** | Portal remarks and resolution history (for you and the agent) |
| `OFFICER_REMARKS.example.txt` | Yes | Template for `OFFICER_REMARKS.txt` |
| `sources/` | **No** | Raw documents (passport, statements, etc.) |
| `ready/` | **No** | Generated upload files |
| `LEARNINGS.md` | Yes | Case lessons: remarks, linkage, portal behaviour |
| `PRINCIPLES.md` | Yes | Portal rules and document standards |
| `WORKFLOW.md` | Yes | Man-in-the-loop process with an AI agent |
| `AGENTS.md` | Yes | Agent instructions (translation, explanations, context) |

## What the pipeline does

- **Bank statements** — picks the salary page via OCR, highlights credits, adds USD→AED notes, sequential naming (`01_Statement_Dec2025.pdf`)
- **Identity** — residence visa, Emirates ID (both sides on one page), work permit (both sides, cropped/rotated)
- **Employment contract** — extracts first, salary, and signature pages (indices in config)
- **Other PDFs** — compress to &lt; 1 MB, optional multi-page stacking
- **Photo** — JPEG compression under size limit

## Customising for a new applicant

1. Copy `config.example.yaml` → `config.yaml`
2. Update `applicant.slug` and all paths under `sources/`
3. Set `employment_contract` page numbers (open the PDF and count from 0)
4. Tune `bank_statements.employer_salary_patterns` and `account_pattern` for OCR
5. Adjust `missing_salary_explanation` if payroll timing needs explanation
6. Run `python prepare.py` and review `ready/` before uploading

Use an AI agent (Cursor, etc.) to **translate remarks**, draft English explanations, and iterate on fixes — see `WORKFLOW.md` and `AGENTS.md`.

## Further reading

- [LEARNINGS.md](LEARNINGS.md) — remark patterns, linkage strategy, portal tips
- [PRINCIPLES.md](PRINCIPLES.md) — upload constraints and naming conventions
- [WORKFLOW.md](WORKFLOW.md) — remark handling, cover letters, collaboration pattern
