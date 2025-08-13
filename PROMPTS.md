# PROMPTS

This file documents how AI assistance was used during development of **SplitBucks**—what I asked, what came back, and how I integrated (or adapted) the results. The goal is transparent use of modern tools while making clear that I owned the design, code, and verification.

## Why include this
- Disclose AI queries used during development.
- Explain how suggestions shaped the solution.
- Show the engineering judgment applied before anything shipped.

## How I use AI (principles)
- **Augment** I use AI for brainstorming, cross-checks, and first drafts. I review, adapt, and test everything.
- **Own the outcome.** All merged code and architectural decisions are mine.
- **Prefer clarity & correctness.** Adopt ideas that improve REST semantics, idempotency, and testability; revise or reject others.
- **No sensitive data.** Only project-local context was shared.

## Tools
- Conversational coding assistant (LLM) for design review, small refactors, and test scaffolding.
- Local dev tools (`flask`, `pytest`) to validate behavior end-to-end.

---

## Selected prompts & outcomes

### 1) REST shape & idempotency
**Prompt (excerpt):**  
> “Refactor action-style endpoints into a more RESTful API. When should I use PUT vs POST? Make deletes idempotent with correct status codes.”

**Outcome:**  
- Switched to resourceful routes:  
  - `PUT /api/users/:name/price` (idempotent upsert; **201** create, **200** update)  
  - `DELETE /api/users/:name` (**204** even if already deleted)  
  - `DELETE /api/history` (**204**)  
  - Kept `POST /api/run` (non-idempotent action)  
- Result: safer retries and simpler client logic.

---

### 2) Prevent reseeding on reads
**Prompt (excerpt):**  
> “After deleting the last user and refreshing state, defaults reappear. Why is `/api/state` reseeding?”

**Outcome:**  
- Made `/api/state` **pure read-only** (no writes).  
- `_ensure_defaults()` now **seeds only if files are missing**, never when empty.  
- Result: reading state no longer mutates data; no “resurrected” defaults.

---

### 3) Case-insensitive names (Bob vs BOB)
**Prompt (excerpt):**  
> “Avoid duplicates like ‘bob’ and ‘BOB’. Should I canonicalize or reject different-case duplicates?”

**Outcome:**  
- Implemented case-insensitive lookup with canonical stored key.  
- Documented policy choice: either **canonicalize** or return **409 Conflict** if different-casing duplicate is attempted.  
- Added optional response flags (`created`, `updated`, `canonicalized`) for UX clarity.

---

### 4) Tests & isolated data
**Prompt (excerpt):**  
> “Provide pytest fixtures that isolate `DATA_DIR`, ensure history header, and cover state/next/run/reset/delete flows.”

**Outcome:**  
- Fixtures point `DATA_DIR` to a per-test temp dir; `ensure_history()` guarantees CSV header.  
- Integration tests cover: `/api/state`, `/api/next`, `/api/run`, idempotent deletes, balance reset, and no-reseed after last delete.

---


## How AI input was integrated
- Converted suggestions into small commits I reviewed and tested.
- Adjusted for project constraints (Python version, file layout).
- Wrote/updated tests to lock behavior and prevent regressions.

## Ownership
AI accelerated parts of the workflow, but I authored the final design and code, decided on the REST/HTTP semantics, implemented the ledger logic and storage behavior, and validated everything with tests and manual QA.

