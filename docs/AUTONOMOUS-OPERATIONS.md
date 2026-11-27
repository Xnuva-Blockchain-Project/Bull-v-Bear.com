# Autonomous operations — mandatory design policy

27 November 2026. Bull v Bear must require no routine backend administration. Replace the proposed administration dashboard with automated health monitoring and read-only public service statistics. Emergency intervention remains available to authorised operators, but no routine manual claim approvals, funding, payout processing or reconciliation.

## Required automation

- Discover and reconcile matured mining rewards in isolated per-currency treasuries; never treat immature or orphaned rewards as spendable.
- Compute bounded claim amounts from verified available reserves, pending obligations, transaction fees and approved reserve policy. Suspend intake when unsafe; no borrowing from other treasuries.
- Validate receiving addresses, enforce cooldown and abuse controls, reserve funds atomically, process queues and maintain durable audit evidence.
- Reconcile uncertain broadcasts before retrying; never blindly resend. Recover persistent queues and accounting after restart. Revalidate after chain reorganisations.
- Automatically pause on stale chain data, wallet outages, inconsistent accounting or insufficient funds. Resume only after defined health and reconciliation gates pass; critical or ambiguous failures remain latched and generate actionable alerts.
- Monitor certificate renewal, disk capacity, service health, queue age and treasury reconciliation; deduplicate alerts. Public statistics must not expose credentials, private records or management endpoints.
- Keep signing credentials and wallet RPC isolated from public web processes. Retain restricted emergency stop and recovery procedures, not a routine administration UI.

## Qualification

BVB-013 is now autonomous health monitoring and recovery, not an administration dashboard. Tests must cover normal operation, resource exhaustion, outages, concurrency, restart, ambiguous payments, reorgs and safe pause/resume. Require sustained operation and real-network qualification before live payments. The current simulation is only a foundation; these requirements are not implemented or qualified by this documentation commit. No production changes authorised. Proposed mining-time split remains 35/35/30, not activated.
