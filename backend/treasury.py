"""Pure offline treasury policy; no wallet, network or production integration."""
from dataclasses import dataclass
from backend.adapters import CURRENCIES

LIMIT = 10**15

def units(value):
    if type(value) is not int or not 0 <= value <= LIMIT:
        raise ValueError("invalid synthetic units")
    return value

@dataclass(frozen=True)
class TreasurySnapshot:
    currency: str
    mature: int
    immature: int = 0
    orphaned: int = 0
    queued: int = 0
    fees: int = 0
    reserve: int = 0
    healthy: bool = False

    def __post_init__(self):
        if self.currency not in CURRENCIES:
            raise ValueError("unknown currency")
        for name in ("mature", "immature", "orphaned", "queued", "fees", "reserve"):
            units(getattr(self, name))
        if type(self.healthy) is not bool:
            raise ValueError("invalid health flag")

    @property
    def available(self):
        return max(0, self.mature - self.queued - self.fees - self.reserve)

    def quote(self, minimum, maximum, divisor=100):
        units(minimum)
        units(maximum)
        if not 0 < minimum <= maximum or type(divisor) is not int or divisor < 1:
            raise ValueError("invalid synthetic payout policy")
        if not self.healthy or self.currency != "DZUV":
            return 0
        amount = min(maximum, self.available // divisor)
        return amount if amount >= minimum else 0

def quotes(snapshots, minimum, maximum, divisor=100):
    result = {}
    for snapshot in snapshots:
        if snapshot.currency in result:
            raise ValueError("duplicate currency snapshot")
        result[snapshot.currency] = snapshot.quote(minimum, maximum, divisor)
    return result
