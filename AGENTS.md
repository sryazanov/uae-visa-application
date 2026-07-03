# Agent context

When working in this repository, read these files first:

1. **`OFFICER_REMARKS.txt`** — current and past GDRFA portal remarks (gitignored; may be missing until the user copies `OFFICER_REMARKS.example.txt`)
2. **`config.yaml`** — case-specific paths, page indices, and explanation text (gitignored)
3. **`PRINCIPLES.md`** — document rules and naming conventions
4. **`CHECKLIST.md`** — required documents and GDRFA portal links
5. **`LEARNINGS.md`** — remark diagnosis, linkage strategy, portal behaviour
6. **`WORKFLOW.md`** — man-in-the-loop process

Generated uploads live in `ready/` (gitignored). Source documents live in `sources/` (gitignored).

## Translation

Portal remarks are usually in **Arabic** and may be garbled or concatenated. The agent should:

1. **Translate remarks** — read the raw text in `OFFICER_REMARKS.txt`, produce a clear **English `# Summary`** for each timestamp block, and call out OCR noise or duplicate phrases when the meaning is ambiguous.
2. **Explain requirements** — tell the applicant in plain English what the officer is actually asking for. Use the remark-to-requirement table in `LEARNINGS.md` §1. For jurisdiction remarks (e.g. DWTCA contract), apply the **linkage strategy** in `LEARNINGS.md` §1.
3. **Draft explanations on documents** — write or revise English text that officers will read:
   - `missing_salary_explanation` in `config.yaml` (bank statement EXPLANATION boxes)
   - salary notes and cover / clarification letters in `sources/`
   - resolution notes in `OFFICER_REMARKS.txt`
4. **Use professional, polite English** — formal tone suitable for immigration review; short sentences; no jargon unless it matches portal terminology (e.g. DWTCA, trade licence).
5. **Confirm with the applicant** before regenerating PDFs when explanations change material facts (dates, amounts, jurisdiction claims).

Keep the **raw Arabic remark unchanged** in `OFFICER_REMARKS.txt`; add translation and interpretation only in the `# Summary` / `# Resolution` comment lines below it.

After resolving a remark, update `OFFICER_REMARKS.txt` with English resolution notes and set `# Status: resolved`.
