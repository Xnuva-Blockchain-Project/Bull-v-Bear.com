"""Offline simulation only. No network or wallet RPC."""
import sqlite3
import uuid
from contextlib import contextmanager

from backend.adapters import simulation_adapter
from backend.treasury import TreasurySnapshot, LIMIT, units

class Faucet:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.wallet = simulation_adapter("DZUV")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS treasury (
          id INTEGER PRIMARY KEY CHECK(id=1), funds INTEGER NOT NULL CHECK(funds>=0));
        INSERT OR IGNORE INTO treasury VALUES (1,0);
        CREATE TABLE IF NOT EXISTS claims (
          id TEXT PRIMARY KEY, address TEXT NOT NULL, created INTEGER NOT NULL,
          amount INTEGER NOT NULL CHECK(amount>0),
          status TEXT NOT NULL CHECK(status IN ('queued','simulated')),
          receipt TEXT UNIQUE);
        CREATE INDEX IF NOT EXISTS claim_address ON claims(address,created);
        CREATE TABLE IF NOT EXISTS simulation_policy (
          id INTEGER PRIMARY KEY CHECK(id=1), healthy INTEGER NOT NULL CHECK(healthy IN (0,1)),
          reserve INTEGER NOT NULL, fees INTEGER NOT NULL,
          minimum INTEGER NOT NULL, maximum INTEGER NOT NULL, divisor INTEGER NOT NULL);
        INSERT OR IGNORE INTO simulation_policy VALUES (1,0,0,0,1,100,100);
        """)

    @contextmanager
    def transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise

    def configure_simulation(self, *, healthy, reserve=0, fees=0,
                             minimum=1, maximum=100, divisor=100):
        # Test harness inputs only, never a public or production endpoint.
        TreasurySnapshot("DZUV",0,fees=fees,reserve=reserve,healthy=healthy).quote(minimum,maximum,divisor)
        if divisor > LIMIT:
            raise ValueError("invalid divisor")
        with self.transaction():
            self.db.execute("UPDATE simulation_policy SET healthy=?,reserve=?,fees=?,minimum=?,maximum=?,divisor=? WHERE id=1",
                            (int(healthy),reserve,fees,minimum,maximum,divisor))

    def fund(self, amount):
        if type(amount) is not int or not 0 < amount <= 10**12:
            raise ValueError("invalid simulated funding")
        with self.transaction():
            # Bound lifetime funding, including already processed claims.
            funds = self.db.execute("SELECT funds FROM treasury WHERE id=1").fetchone()[0]
            used = self.db.execute("SELECT COALESCE(SUM(amount),0) FROM claims").fetchone()[0]
            if funds + used + amount > LIMIT:
                raise ValueError("synthetic treasury limit")
            self.db.execute("UPDATE treasury SET funds=funds+? WHERE id=1", (amount,))

    def _snapshot(self):
        funds = self.db.execute("SELECT funds FROM treasury WHERE id=1").fetchone()[0]
        totals = dict(self.db.execute("SELECT status,SUM(amount) FROM claims GROUP BY status"))
        queued = totals.get("queued",0)
        healthy,reserve,fees,minimum,maximum,divisor = self.db.execute(
            "SELECT healthy,reserve,fees,minimum,maximum,divisor FROM simulation_policy WHERE id=1").fetchone()
        # funds already excludes queued claims; add them back exactly once.
        snapshot = TreasurySnapshot("DZUV",funds+queued,queued=queued,fees=fees,reserve=reserve,healthy=bool(healthy))
        return snapshot, (minimum,maximum,divisor), totals

    def claim(self, currency, address, now):
        if currency != "DZUV" or not self.wallet.validate(address):
            raise ValueError("unsupported currency or simulated address")
        if type(now) is not int or not 0 <= now <= LIMIT:
            raise ValueError("invalid simulation clock")
        with self.transaction():
            if self.db.execute("SELECT 1 FROM claims WHERE address=? AND created>?", (address,now-86400)).fetchone():
                raise ValueError("cooldown")
            snapshot, policy, _ = self._snapshot()
            amount = snapshot.quote(*policy)
            if not amount:
                raise ValueError("claims suspended or insufficient simulated funds")
            if self.db.execute("UPDATE treasury SET funds=funds-? WHERE id=1 AND funds>=?", (amount,amount)).rowcount != 1:
                raise ValueError("insufficient simulated funds")
            claim_id = uuid.uuid4().hex
            self.db.execute("INSERT INTO claims VALUES (?,?,?,?,'queued',NULL)", (claim_id,address,now,amount))
        return claim_id

    def process(self, claim_id):
        with self.transaction():
            row = self.db.execute("SELECT status,receipt FROM claims WHERE id=?", (claim_id,)).fetchone()
            if row is None:
                raise ValueError("unknown claim")
            if row[0] == "simulated":
                return row[1]
            snapshot, _, _ = self._snapshot()
            if not snapshot.healthy or snapshot.mature < snapshot.queued + snapshot.reserve + snapshot.fees:
                raise ValueError("payments suspended")
            receipt = self.wallet.receipt(claim_id)
            self.db.execute("UPDATE claims SET status='simulated',receipt=? WHERE id=?", (receipt,claim_id))
            return receipt

    def summary(self):
        with self.transaction():
            snapshot, _, totals = self._snapshot()
            return {"available": snapshot.available, "queued": totals.get("queued",0), "simulated": totals.get("simulated",0)}

    def close(self):
        self.db.close()
