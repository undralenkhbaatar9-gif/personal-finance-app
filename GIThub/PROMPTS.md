# Build prompts — Personal Finance Tool

## How to use this (read once)

1. Put `AGENT_SPEC.md` in the project root. It holds the whole design, so the prompts stay short.
2. Run the prompts **in order**, **one new chat per prompt**. A fresh chat costs less usage and the agent doesn't get confused by old messages.
3. In every chat, attach (or paste) **only** the files listed under *Attach*. Agents that can read your folder (Copilot agent mode in VS Code, Gemini CLI) just need the file names.
4. After each prompt, run the *Check*. Pass → next prompt. Fail → use the **Fix prompt** at the bottom. Don't argue in the same chat for more than 2 rounds; start a new chat with the Fix prompt.
5. Commit after every passing step: `git add -A && git commit -m "P<n> done"`. If an agent breaks things, `git checkout .` and retry.

**Privacy:** never paste your real bank statement into a free AI chat (free tiers may use it for training). The tests build a fake statement instead. Keep real statements outside the project folder or in a `.gitignore`d `private/` folder.

**Which agent where (suggestion):**
- Agents that write files themselves (Copilot agent mode, Gemini CLI): best for everything; use them especially for P5–P8.
- Chat-only (ChatGPT, Gemini web): fine for single-file prompts; copy the code blocks into the files yourself.
- Hardest steps (P5 importer, P7 classifier): use the strongest model you have quota for.

---

## P0 — Manual setup (no AI)

```bash
# 1. Install PostgreSQL 15+ (remember the postgres password), then:
psql -U postgres -c "CREATE DATABASE finance;"
psql -U postgres -c "CREATE DATABASE finance_test;"
# 2. Project folder
mkdir finance-tool && cd finance-tool
git init
mkdir private   # real statements + test files; git-ignored
python -m venv .venv
# Windows: .venv\Scripts\activate     Mac/Linux: source .venv/bin/activate
# 3. Copy AGENT_SPEC.md and PROMPTS.md into this folder
```

---

## P1 — Skeleton and DB connection

Attach: `AGENT_SPEC.md`

```
Read AGENT_SPEC.md. Follow §12.
Create exactly these files: requirements.txt (pin major versions), .env.example (DATABASE_URL, TEST_DATABASE_URL), .gitignore (.venv, .env, __pycache__, private/, *.xlsx except tests/fixtures), finance/__init__.py, finance/config.py, finance/db.py, run.bat, run.sh, app.py.
db.py: engine from config, SessionLocal, get_session() contextmanager that commits/rolls back, and Base = DeclarativeBase subclass.
app.py: st.set_page_config(title "Finance", wide), title, one line telling the user to use the sidebar pages, and a "DB connected ✓" / error message using a SELECT 1.
run.bat/run.sh: activate .venv, run `streamlit run app.py`.
Output only the files.
```

Check: `pip install -r requirements.txt`, copy `.env.example` to `.env` and fill it in, then `streamlit run app.py` shows "DB connected ✓".

---

## P2 — Models

Attach: `AGENT_SPEC.md`, `finance/db.py`

```
Read AGENT_SPEC.md §4 and §12. Write finance/models.py with SQLAlchemy 2.0 typed models for all 7 tables exactly as specified (names, types, constraints, CheckConstraints, unique constraints, indexes, relationships). Import Base from finance/db.py. Use Numeric(16,2) with Decimal. Output only finance/models.py.
```

Check: `python -c "import finance.models as m; print(sorted(m.Base.metadata.tables))"` lists 7 tables.

---

## P3 — Alembic, seed data

Attach: `AGENT_SPEC.md`, `finance/models.py`, `finance/config.py`

```
Read AGENT_SPEC.md §10 and §12.
1. Give me the exact shell commands to init Alembic in ./migrations and autogenerate the first migration.
2. Output migrations/env.py edited to use DATABASE_URL from finance.config and target_metadata = Base.metadata (import finance.models).
3. Output seed/categories.yaml (exact lists from §10; transfer categories in_reports: false; include the seed rule and the khan bank).
4. Output finance/seed.py: idempotent seed() that upserts banks, categories, the seed rule; runnable as `python -m finance.seed`.
Output only commands + files.
```

Check: `alembic upgrade head` then `python -m finance.seed` twice → no errors, no duplicate rows (`SELECT count(*) FROM categories;` = 33).

---

## P4 — Khan Bank parser + tests

Attach: `AGENT_SPEC.md`

```
Read AGENT_SPEC.md §5, §6, §12.
Write: finance/parsers/base.py (StdTxn, StatementInfo, BankParser, to_decimal), finance/parsers/khan.py (KhanParser, openpyxl, read_only, data_only), finance/parsers/__init__.py (PARSERS dict).
Write tests/conftest.py with a plain function `build_khan_xlsx(path, rows=None)` (reusable outside pytest) and a fixture `khan_xlsx(tmp_path)` that calls it. It builds a fake Khan statement with openpyxl matching §6 exactly: row 1 info cells (IBAN "IBAN: MN660005005954230716", period cells "2026/08/14" and "2026/10/14", "MNT"), row 2 headers in Cyrillic, 5 data rows (credits as strings with thousands commas like "150,000.00", debits negative, consistent running balances, one row with empty counterparty and branch 5000), an empty row, then a totals row.
Write tests/test_khan_parser.py: detect() true; account_no == "5954230716"; 5 txns; amounts Decimal and signed correctly; totals parsed; balances chain; to_decimal edge cases ("", None, "1,234.50", -93.76).
No DB in these tests. Output only the files.
```

Check: `pytest tests/test_khan_parser.py -q` → all pass.

---

## P5 — Importer

Attach: `AGENT_SPEC.md`, `finance/models.py`, `finance/db.py`, `finance/parsers/base.py`, `tests/conftest.py`

```
Read AGENT_SPEC.md §7, §8 (only the function signatures), §12.
Write finance/importer.py: ImportResult dataclass, DuplicateFileError, ValidationError(errors: list[str]), import_statement(path, file_name, bank_code, session=None).
Use postgresql insert(...).on_conflict_do_nothing(index_elements=["account_id","fingerprint"]).returning(id) to count new rows.
Call finance.counterparty.attach_counterparties(session, txn_ids, bank_code) and finance.classifier.classify_transactions(session, txn_ids) after insert (these modules come later; import them inside the function).
Also write finance/counterparty.py and finance/classifier.py as STUBS only: attach_counterparties and classify_transactions that do nothing (pass), so tests run now.
Update tests/conftest.py (keep build_khan_xlsx; let it accept custom rows) and add a `db_session` fixture using TEST_DATABASE_URL, create_all before / drop_all after, and seed().
Write tests/test_importer.py: first import → rows_new 5; same file again → DuplicateFileError; a second file with 3 overlapping + 2 new rows → rows_new 2, rows_duplicate 3; a file with a broken balance → ValidationError and zero rows saved.
Output only the files.
```

Check: `pytest -q` → all pass.

---

## P6 — Counterparties

Attach: `AGENT_SPEC.md`, `finance/models.py`, `finance/counterparty.py`

```
Read AGENT_SPEC.md §8, §12. Replace the stub finance/counterparty.py with the real one: POS_PATTERNS dict (khan: []), normalise_merchant(), extract_match_key(), get_or_create_counterparty(), attach_counterparties(session, txn_ids, bank_code) which sets transactions.counterparty_id for those ids (set first_seen to earliest txn date).
Write tests/test_counterparty.py: acct key; system key with branch 5000; system:unknown; a POS case by temporarily adding a pattern r"^POS\s+(.+)" to POS_PATTERNS["khan"] via monkeypatch: "POS CU 25 SUKHBAATAR 2026-09-03 1234****5678" → "pos:CU 25 SUKHBAATAR".
Output only the files.
```

Check: `pytest -q` → all pass.

---

## P7 — Classifier

Attach: `AGENT_SPEC.md`, `finance/models.py`, `finance/classifier.py`

```
Read AGENT_SPEC.md §9, §12. Replace the stub finance/classifier.py with the real one: classify_transactions(session, txn_ids=None) (None = all non-manual rows), the 4-step order exactly, transfer pair detection (10 min, same abs amount, opposite sign, two different own accounts), rule matching helper match_rule(rule, txn, match_key) -> bool, and test_rule(session, rule_dict) -> pandas DataFrame (date, amount, description, counterparty_account, current category) of matches, max 500 rows.
Write tests/test_classifier.py (use db_session fixture; insert rows directly): manual never changes; own-account counterparty → transfer; counterparty default applies; ask_per_txn skips default; rule priority order; amount_sign filter; seed rule puts branch 5000 debit into "Bank fees & charges"; pair detection marks both sides.
Output only the files.
```

Check: `pytest -q` → all pass.

---

## P8 — Import page

Attach: `AGENT_SPEC.md` (§11 enough), `finance/importer.py`, `finance/parsers/__init__.py`

```
Read AGENT_SPEC.md §11 (Import) and §12. Write pages/1_Import.py.
Flow: select bank from PARSERS → st.file_uploader(.xlsx) → save to a temp file → parse for preview (StatementInfo + first 20 rows as DataFrame + validation errors if any, via a validate-only helper you add to importer.py as validate(info, txns) -> list[str]) → Confirm button → import_statement → st.success with counts and a link hint to the Review page. Show DuplicateFileError / ValidationError nicely. Below: table of past imports (newest first).
Output pages/1_Import.py and the full updated finance/importer.py.
```

Check: make a fake file with `python -c "from tests.conftest import build_khan_xlsx; build_khan_xlsx('private/fake.xlsx')"`, import it on the page, then import it again → duplicate message. Then import your real statement (it stays on your PC).

---

## P9 — Review page

Attach: `AGENT_SPEC.md` (§11), `finance/models.py`, `finance/classifier.py` (signatures only is fine)

```
Read AGENT_SPEC.md §11 (Review) and §12. Write pages/2_Review.py.
Query counterparties that have ≥1 transaction with category_source='unclassified'; aggregate txns, in, out, 3 distinct sample descriptions; sort by in+out desc.
st.data_editor with the columns in §11; category column = SelectboxColumn of "kind: name" strings (map back to id). Save button: update counterparties (display_name, default_category_id, is_own_account, ask_per_txn), then classify_transactions on their transaction ids, then st.rerun(). Show "All classified 🎉" when empty. Put the unclassified count in st.sidebar.
Output only pages/2_Review.py.
```

Check: after an import, the Review page lists counterparties; marking one as own account moves its rows to Transfer.

---

## P10 — Transactions page

Attach: `AGENT_SPEC.md` (§11), `finance/models.py`

```
Read AGENT_SPEC.md §11 (Transactions) and §12. Write pages/3_Transactions.py.
Filters in sidebar. Load max 2000 rows. st.data_editor: date, account nickname/no, amount (formatted), description, counterparty display_name or match_key, category (SelectboxColumn "kind: name"), source (ro), note, "make rule" checkbox. Save: rows whose category or note changed → update, set category_source='manual' when category changed; rows with "make rule" ticked → create rule field='match_key', match_type='equals', pattern=the row's match_key, category=chosen, priority 50. Show how many rows saved.
Output only pages/3_Transactions.py.
```

Check: change one category → source shows `manual`; re-run a classify (re-import another file) → it stays.

---

## P11 — Settings page

Attach: `AGENT_SPEC.md` (§11), `finance/models.py`, `finance/classifier.py`

```
Read AGENT_SPEC.md §11 (Settings) and §12. Write pages/5_Settings.py with st.tabs: Accounts, Categories, Rules, Backup.
Accounts: data_editor (nickname, is_own). Categories: data_editor + add form (kind, name, in_reports); no delete if used. Rules: data_editor (priority, field, match_type, pattern, amount_sign, category, active) + add form + "Test rule" button showing test_rule() result count and table + "Re-classify all" button (classify_transactions(session, None)). Backup: folder text input, button runs pg_dump via subprocess with the DATABASE_URL parts (PGPASSWORD env), output file finance_YYYYmmdd_HHMM.dump (-Fc); show stderr on failure and a hint if pg_dump isn't found.
Output only pages/5_Settings.py.
```

Check: add a rule, Test it, Re-classify all; Backup creates a `.dump` file.

---

## P12 — Reports

Attach: `AGENT_SPEC.md` (§11), `finance/models.py`

```
Read AGENT_SPEC.md §11 (Reports) and §12. Write finance/reports.py (pure query functions, each takes session, date_from, date_to, include_transfers=False and returns a DataFrame: monthly_summary, expense_by_category, income_by_category, top_counterparties(n=10), transactions_export) and pages/4_Reports.py (date range default = last 6 months; metrics row: income, expense, net, savings rate; plotly grouped bar monthly income vs expense; horizontal bar expense by category + table; top counterparties table; CSV and XLSX download buttons via BytesIO). Exclude categories with in_reports=false and unclassified rows unless toggled (show unclassified total as a warning).
Output only the two files.
```

Check: numbers on the page match `SELECT sum(amount) ...` for one month you pick.

---

## P13 — README and final check

Attach: `AGENT_SPEC.md`, the file list (`git ls-files`)

```
Read AGENT_SPEC.md. Write README.md: what the app does (3 lines), setup (Postgres, venv, .env, alembic upgrade head, python -m finance.seed), run (run.bat / run.sh), monthly routine (download statement → Import → Review → Reports), backup & restore (pg_restore command), how to add a new bank (steps in "New bank prompt" below), running tests. Max 120 lines. Output only README.md.
```

Check: follow the README on a clean copy of the folder.

---

## Fix prompt (use whenever a Check fails)

Attach: `AGENT_SPEC.md`, the failing file(s), the test file if any

```
Read AGENT_SPEC.md §12. This command fails:
<paste the command>
Error (last 30 lines):
<paste only the end of the traceback>
Fix the bug with the smallest change. Don't change public names or other files unless the error is in them. Output only the full corrected file(s).
```

---

## New bank prompt (later)

Attach: `AGENT_SPEC.md`, `finance/parsers/base.py`, `finance/parsers/khan.py` (as an example)

```
Read AGENT_SPEC.md §5, §12. Write finance/parsers/<code>.py for <Bank name>.
Its statement format (anonymised, numbers changed): <describe rows/columns, or paste 5 fake rows with the real layout>.
Also output the updated finance/parsers/__init__.py and tests/test_<code>_parser.py with a fake-file fixture like the Khan one. Add the bank to seed/categories.yaml banks list.
Output only the files.
```

## Finish POS merchants (when you have a statement with card purchases)

Attach: `finance/counterparty.py`

```
Khan Bank card-payment descriptions look like these (anonymised):
<paste 5–10 descriptions>
Add regexes to POS_PATTERNS["khan"] that capture the merchant name so the same shop always gets the same key. Add these examples to tests/test_counterparty.py. Output only the two files.
```
