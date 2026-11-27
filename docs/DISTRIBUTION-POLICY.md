# Faucet distribution policy — mining first

User requirement: no more than one whole coin distributed in any 24-hour period; distribute fractions when treasury funds are low. The faucet must not undermine mining.

Engineering interpretation: aggregate across all claimants, independently per cryptocurrency, in a rolling 24-hour window, not a calendar-day reset or per-address allowance. Confirm this interpretation before production qualification. No unused allowance carryover. Convert the one-coin ceiling to exact integer units using each qualified currency's denomination metadata; never assume all currencies share a precision.

Proposed (not approved) additional policy: daily budget at most 10% of available treasury or one coin, whichever is smaller, and individual claim at most 0.01 coin or 1% of that budget, whichever is smaller. Round down to integer units. Fees and protected reserves are separate constraints; suspend if economically or operationally unsafe.

Implementation gate: atomically account for outstanding reservations and actual payouts; pending claims must not age out of the cap before payment. Recheck rolling payout history at execution, preserve timestamps and reservations across restarts, and reconcile ambiguous broadcasts before retry. Use trusted time; fail closed on clock anomalies. Test simultaneous claims, exact 24-hour boundary, delayed payments, restart, fractional balances, exhaustion, independent currency limits and fee/reserve protection. No real payouts, production changes or mining allocation changes authorised. Current synthetic engine does not yet enforce this aggregate cap; implementation and regression qualification required before progressing to live integration.
