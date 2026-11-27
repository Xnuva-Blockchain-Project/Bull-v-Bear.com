"""Offline supply-adjusted policy. No approved production currency limits."""
from dataclasses import dataclass

WINDOW = 86400

def integer(n):
    if type(n) is not int or n < 0:
        raise ValueError("expected nonnegative integer")
    return n

@dataclass(frozen=True)
class DistributionPolicy:
    original_supply: int
    reference_supply: int
    units_per_coin: int
    hard_ceiling: int
    market_weight: int = 0

    def __post_init__(self):
        for n in (self.original_supply,self.reference_supply,self.units_per_coin,self.hard_ceiling):
            if integer(n) == 0:
                raise ValueError("positive policy inputs required")
        if type(self.market_weight) is not int or self.market_weight != 0:
            raise ValueError("market adjustment disabled")

    @property
    def daily_ceiling(self):
        return min(self.hard_ceiling, self.original_supply * self.units_per_coin // self.reference_supply)

    def quote(self, *, now, available, pending, paid, healthy=False):
        """Pure calculation; caller must atomically reserve and persist.
        paid: iterable of (payment timestamp, integer amount) for this currency.
        pending: total unpaid reservations, regardless of age.
        """
        for n in (now,available,pending):
            integer(n)
        if type(healthy) is not bool:
            raise ValueError("invalid health")
        spent = 0
        for timestamp, amount in paid:
            integer(timestamp)
            integer(amount)
            if timestamp > now:
                raise ValueError("future payment timestamp")
            if timestamp > now-WINDOW:
                spent += amount
        remaining = max(0,self.daily_ceiling-pending-spent)
        # Provisional fixture: 10% treasury budget and 1% individual share.
        # available excludes existing reservations and protected reserves.
        budget = min(self.daily_ceiling,available//10)
        return min(remaining, budget//100) if healthy else 0
