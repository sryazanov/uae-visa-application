# Man-in-the-loop workflow

This repo is a **harness**: repeatable automation plus human (and AI) judgment at the steps that matter.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│ Collect     │ ──▶ │ Configure    │ ──▶ │ Run         │ ──▶ │ Human review │
│ sources/    │     │ config.yaml  │     │ prepare.py  │     │ ready/       │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                                                                    │
                                                                    ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│ Approved    │ ◀── │ Upload to    │ ◀── │ Fix remarks │ ◀── │ Portal       │
│             │     │ GDRFA        │     │ (loop)      │     │ feedback     │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
```

## Roles

| Role | Responsibility |
|------|----------------|
| **Applicant** | Gathers raw documents, verifies accuracy of salary/identity data |
| **Colleague / operator** | Maintains `config.yaml`, runs pipeline, uploads `ready/` |
| **AI agent** | Translates remarks; drafts English explanations; adjusts config, page indices; regenerates after remarks |

## First-time setup (new colleague)

1. Clone this repository.
2. `pip install -r requirements.txt` and install [Tesseract](https://github.com/tesseract-ocr/tesseract).
3. `cp config.example.yaml config.yaml`
4. `cp OFFICER_REMARKS.example.txt OFFICER_REMARKS.txt` — paste portal remarks here as they arrive
5. Create `sources/` and add documents (never commit them).
6. Open each PDF once to confirm paths and page numbers in config.
7. `python prepare.py` → inspect every file in `ready/` visually.
8. Upload to portal. **Note:** you may not have enough upload slots on the first pass — more are often added after remarks ([LEARNINGS.md](LEARNINGS.md) §2).

## Iteration after portal remarks

Typical loop:

1. **Capture the remark** — paste exact officer text into `OFFICER_REMARKS.txt` (timestamp + raw Arabic).
2. **Translate** — ask the agent to add an English `# Summary` under each remark (see `AGENTS.md`).
3. **Diagnose** — identify the checklist item behind the remark ([LEARNINGS.md](LEARNINGS.md) §1); apply linkage strategy if jurisdiction is questioned.
4. **Change the minimum**:
   - New source PDF → drop in `sources/`, update path in `config.yaml`
   - Wrong page extracted → fix `employment_contract` page indices
   - Salary not detected → add `employer_salary_patterns` or `account_pattern`
   - Timing/currency question → edit `missing_salary_explanation` in `config.yaml` (agent drafts English text)
   - Clarification / cover letter → agent drafts English letter in `sources/`, maps to `ready/` filenames
4. **Regenerate** — `python prepare.py` (overwrites `ready/`).
5. **Review** — open changed PDFs; confirm highlights, explanations, file sizes.
6. **Resubmit** — only flagged/editable slots; skip locked files ([LEARNINGS.md](LEARNINGS.md) §5); put clarification letter first.
7. **Close the round** — set `# Status: resolved` in `OFFICER_REMARKS.txt` and note what changed.

### Prompt template for an AI agent

```
I'm preparing UAE Golden Visa documents using the golden-visa harness in this repo.

Read OFFICER_REMARKS.txt for all portal remarks and resolution history.

Current config: config.yaml
Sources are in sources/ (gitignored).

Please:
1. Translate the latest open remark in OFFICER_REMARKS.txt and add/update the English # Summary
2. Explain in plain English what the officer needs
3. Propose minimal config or source changes (including explanation letter text)
4. Run python prepare.py
5. List which ready/ files changed and what to upload
6. Draft English # Resolution notes for OFFICER_REMARKS.txt
```

## When to change code vs config

| Situation | Action |
|-----------|--------|
| Different employer name on statements | `config.yaml` → `employer_salary_patterns` |
| New bank statement date format | Code change in `golden_visa/bank_statements.py` + example config |
| Work permit scanned different rotation | `config.yaml` → `work_permit.rotations` |
| Portal adds new document type | New prepare step in `golden_visa/` + config block |

Prefer **config changes** for one-off cases; promote to **code** when a second colleague hits the same issue.

## Quality checklist before upload

- [ ] Every PDF &lt; 1 MB
- [ ] Bank statements: salary highlighted, AED notes where needed
- [ ] Any gap month has EXPLANATION box
- [ ] EID and work permit: both sides visible on one page
- [ ] Contract: three distinct pages, readable
- [ ] Filenames match what the cover letter references
- [ ] No personal data in committed files (`config.example.yaml` and `OFFICER_REMARKS.example.txt` use placeholders only)
- [ ] No personal documents committed to git (`git status` clean of `sources/`, `config.yaml`, `ready/`, `OFFICER_REMARKS.txt`)

## Sharing improvements

- **Config tips** → extend `config.example.yaml` with comments
- **New portal rules or remark patterns** → update `PRINCIPLES.md` or `LEARNINGS.md`
- **Reusable code** → PR to `golden_visa/`
- **Case learnings** → optional local notes in `SUMMARY.md` (gitignored); promote reusable lessons to `LEARNINGS.md`

Do **not** commit applicant PII, passport scans, or bank statements.
