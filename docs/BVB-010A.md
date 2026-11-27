# BVB-010A — Offline treasury regression qualification

Baseline: `46fea87206bf608b3a9238e6ca4fd0c2013e1ff8`.

Six source/test files verified with git hash-object against connector-retrieved GitHub blobs in an isolated container:

- backend/adapters.py: dc9915a930b8438c73058f203498411e01ee498d
- backend/faucet.py: e4796d48572300fa4c34336fd54aa2dd06bb62e0
- backend/treasury.py: 02f5cbfef108001c72923d0c8346d7b2c24f6679
- tests/test_adapters.py: 53bfd8859cbacc23276ab4ff93c2b4e579c4d967
- tests/test_faucet.py: f0348df32b96689b3207463dfc4190d7daeb19c7
- tests/test_treasury.py: a969f3fa81a7e85817d78ba1fd8b3403c2c3b190

Python 3.13.5. Command: `python3 -m unittest discover -s tests -v`.

```
Ran 17 tests in 0.014s
OK
```

17 passed, 0 failed, 0 skipped. PASS for offline regression scope only. Treasury quote policy is not yet integrated with the claim engine. Automated reward ingestion, durable ledger, atomic quote reservation, health-driven worker controls and real-network qualification remain outstanding. No production systems or wallets accessed. Next: BVB-010B transactional integration.
