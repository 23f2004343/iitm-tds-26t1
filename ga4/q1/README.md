# Q1 — Excel: Operational Margin Consolidation

## Answer

**Total variance (Revenue − Expense) for Onboarding in Europe up to 15 Jul 2024: `455037.98`**

## Steps

1. **Trim & standardise regions** — mapped aliases (`EU`, `E.U.`, `Europa`, `Europe Region`, etc.) to `Europe`.
2. **Parse dates** — handled `YYYY-MM-DD`, `DD/MM/YYYY`, `Mon DD, YYYY`, and quarter codes (`2024 Q1` → `2024-03-31`).
3. **Clean numerics** — stripped `USD`, `$`, spaces, commas. Filled blank/`USD TBD` expense as **37% of revenue**.
4. **Split Ops Notes** on `|` to extract the operations category.
5. **Filtered** for `Onboarding` category + `Europe` region + `Parsed Date ≤ 2024-07-15`.
6. **Summed** `Revenue − Expense` across the 16 matching records.
