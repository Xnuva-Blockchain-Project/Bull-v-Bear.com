"""Offline simulation only. No network or wallet RPC."""
import re
import sqlite3
import uuid
from contextlib import contextmanager

CURRENCIES = {"DZUV": "Denzuve", "AUZV": "Aurzola", "SEZQ": "Sestovi",
              "DPZE": "Duprezo", "ASVR": "Asveru"}

class SimulatedWallet:
    def validate(self, address):
        return isinstance(address, str) and re.fullmatch(r"sim-DZUV-[a-zA-Z0-9]{8,64}", address) is not None

    def receipt(self, claim_id):
        return "simulation-" + claim_id

class Faucet:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.wallet = SimulatedWallet()
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

    def fund(self, amount):
        if type(amount) is not int or not 0 < amount <= 10**12:
            raise ValueError("invalid simulated funding")
        with self.transaction():
            self.db.execute("UPDATE treasury SET funds=funds+? WHERE id=1", (amount,))

    def claim(self, currency, address, now):
        if currency != "DZUV" or not self.wallet.validate(address):
            raise ValueError("unsupported currency or simulated address")
        if type(now) is not int or now < 0:
            raise ValueError("invalid simulation clock")
        amount = 100  # synthetic units only; not a launch policy
        with self.transaction():
            if self.db.execute("SELECT 1 FROM claims WHERE address=? AND created>?", (address,now-86400)).fetchone():
                raise ValueError("cooldown")
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
            receipt = self.wallet.receipt(claim_id)
            self.db.execute("UPDATE claims SET status='simulated',receipt=? WHERE id=?", (receipt,claim_id))
            return receipt

    def summary(self):
        funds = self.db.execute("SELECT funds FROM treasury WHERE id=1").fetchone()[0]
        totals = dict(self.db.execute("SELECT status,SUM(amount) FROM claims GROUP BY status"))
        return {"available": funds, "queued": totals.get("queued",0), "simulated": totals.get("simulated",0)}

    def close(self):
        self.db.close()
