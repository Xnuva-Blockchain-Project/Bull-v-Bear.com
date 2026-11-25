# Bull v Bear — Development roadmap

## BVB-006 — Holding page deployment record

25 November 2026. Production operator reported successful BVB-005 verification: both https://bull-v-bear.com/ and https://www.bull-v-bear.com/ served the exact committed holding page over HTTPS. Apache and MySQL remained active. The former classifieds URL returned HTTP 404. The legacy application and database were preserved separately; four backup checksums passed and the SQL export contained 70 table definitions. Full restoration has not been tested.

Holding page source commit: `01ae0b42d8c7fda0c01aa8110ca4d6d6d9897a7f`.

DNS: restored the missing www CNAME and verified authoritative and public resolution. Targeted Let's Encrypt renewal succeeded for both hostnames; certificate expires 23 February 2027. Future automatic renewal remains to be verified. No mining rotation or wallet changes were part of this deployment.

## Purpose

A mining-funded, automated cryptocurrency faucet that enables newcomers to receive coins directly into their own wallets without purchasing coins or using an exchange. No visitor-device mining. No claims, deposits or live payouts during the holding-page phase.

## Proposed implementation

1. Complete and qualify Denzuve Transition Release 1 before integrating the faucet.
2. Develop a reusable faucet backend and currency adapters, beginning with Denzuve. Use isolated treasury accounting and dedicated receiving/payout wallets.
3. Qualify address validation, matured reward accounting, reserve checks, fee handling, rate limits, abuse prevention, duplicate-payment protection, crash recovery and transaction reconciliation. Keep wallet RPC private and web-facing processes isolated from signing credentials.
4. Integrate with the existing mining rotation only after capacity, compatibility and operational tests. Proposed mining-time allocation: development 35%, XNUVA Game 35%, Bull v Bear faucet 30%. This is a proposal, not deployed configuration; duration and per-currency scheduling remain to be determined. Mining time does not guarantee equivalent revenue shares.
5. Test on isolated infrastructure before enabling real payouts. Publish transparent statistics and verification links to EZHScan. Provide wallet and independent-node guidance through EuropaZeus.
6. Extend to the remaining four currencies as each modernisation and faucet adapter qualifies.

## Operating principles

No chain resets, no changes to monetary policy for faucet funding, no commingling of development, game and faucet funds, no unrestricted wallet access from the public website. Preserve existing services and avoid unnecessary new infrastructure. Suspend claims or payouts safely when funds or network health are insufficient. No launch date or guaranteed rewards.

## Outstanding checks

Independent external website verification; future certificate renewal; full legacy backup restoration test; backend design and qualification. Private operational records and credentials must not be committed to this public repository.
