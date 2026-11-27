"""Provisional planning references; not consensus-verified or live configuration."""
from types import MappingProxyType
from backend.distribution import DistributionPolicy

REFERENCE_SUPPLY = 4_200_000
PROVISIONAL_SUPPLIES = MappingProxyType({
    "AUZV": 4_200_000,
    "DZUV": 21_000_000,
    "SEZQ": 40_000_000,
    "DPZE": 50_000_000,
    "ASVR": 110_000_000,
})

def simulation_policy(currency, units_per_coin):
    # Precision must be explicitly supplied; no implied consensus metadata.
    if currency not in PROVISIONAL_SUPPLIES:
        raise ValueError("unknown currency")
    if type(units_per_coin) is not int or units_per_coin <= 0:
        raise ValueError("invalid denomination")
    supply = PROVISIONAL_SUPPLIES[currency]
    ceiling = supply * units_per_coin // REFERENCE_SUPPLY
    return DistributionPolicy(supply, REFERENCE_SUPPLY, units_per_coin, ceiling)
