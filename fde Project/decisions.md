# Level 0: Desk Readback & Decisions

## 1. Data Flow
[Sources: CSV, HTML, JSONL, XLSX] --> [Ingestion Service (Pandas)] --> [Normalization & Type Casting (Integer for Paise)] --> [SQLite Database (Idempotent Storage)] --> [Reconciliation Engine] --> [Case Generation] --> [FastAPI Backend] <--> [React Frontend (RBAC filtered)]

## 2. Source Authority
- **Internal Ledger & Holdings:** Primary source for broker's presumed state.
- **DP Extract & Bank Confirmations:** External authoritative evidence for settlement and actual cash.

## 3. Cases that must stay `UNKNOWN`
1. A bank confirmation row with a duplicated or missing UTR/reference where the client identity cannot be definitively matched.
2. An internal holding where the DP extract is completely missing (stale cut) for that specific ISIN and date, making it impossible to confidently say it settled.

## 4. Five Clarification Questions for Operations
1. If a DP movement is 'PENDING', do we expect it to settle at the next cut, or does it require manual follow-up with the depository?
2. Are corporate actions (like bonuses or splits) reflected directly in the internal holdings snapshot before the DP extract confirms them?
3. What is the exact timezone for the `cut_at` timestamps across different exchange feeds and internal ledgers?
4. If a client's status changes (e.g., account frozen) between the internal snapshot and the DP extract, how should the discrepancy be flagged?
5. For public regulatory circulars, which specific operations team acts as the final approver before a rule impacts case severity?

## 5. Architectural & Implementation Decisions
- **Tech Stack:** FastAPI (for async & Pydantic validation) and React + Tailwind (for a lightweight read-only UI without complex state overhead).
- **Data Handling:** Financial amounts are calculated in integer units (paise) to avoid floating-point inaccuracies.
- **Database:** SQLite chosen for zero-config local testing and idempotent storage capabilities.
- **Business Rule:** PENDING states in DP files are strictly ignored (treated as 0 settled quantity) as they cannot be counted as settled inventory.