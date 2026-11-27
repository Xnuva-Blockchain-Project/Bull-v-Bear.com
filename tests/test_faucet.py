import unittest
import tempfile
from pathlib import Path
from backend.faucet import Faucet

class FaucetTests(unittest.TestCase):
    def setUp(self):
        self.f = Faucet()
        self.f.configure_simulation(healthy=True, minimum=100, maximum=100, divisor=1)
        self.f.fund(200)
        self.address = "sim-DZUV-abcdefgh"

    def tearDown(self):
        self.f.close()

    def test_claim_and_idempotent_payment(self):
        c = self.f.claim("DZUV", self.address, 100000)
        self.assertEqual(self.f.summary(), {"available":100,"queued":100,"simulated":0})
        r = self.f.process(c)
        self.assertEqual(r,self.f.process(c))
        self.assertEqual(self.f.summary(), {"available":100,"queued":0,"simulated":100})

    def test_cooldown(self):
        self.f.claim("DZUV",self.address,100000)
        with self.assertRaises(ValueError):
            self.f.claim("DZUV",self.address,100001)
        self.f.claim("DZUV",self.address,186400)

    def test_invalid_address_and_currency(self):
        for coin,address in [("AUZV",self.address),("DZUV","real-address")]:
            with self.assertRaises(ValueError):
                self.f.claim(coin,address,100000)
        self.assertEqual(self.f.summary()["available"],200)

    def test_exhaustion(self):
        for address in [self.address,"sim-DZUV-ijklmnop"]:
            self.f.claim("DZUV",address,100000)
        with self.assertRaises(ValueError):
            self.f.claim("DZUV","sim-DZUV-qrstuvwx",100000)
        self.assertEqual(self.f.summary()["available"],0)

    def test_invalid_funding(self):
        for amount in [-1,0,1.5,True]:
            with self.assertRaises(ValueError):
                self.f.fund(amount)

    def test_restart(self):
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d)/"simulation.db")
            f = Faucet(path)
            f.configure_simulation(healthy=True, minimum=100, maximum=100, divisor=1)
            f.fund(100)
            c = f.claim("DZUV",self.address,100000)
            f.close()
            f = Faucet(path)
            try:
                self.assertEqual(f.summary()["queued"],100)
                self.assertEqual(f.process(c),f.process(c))
                self.assertEqual(f.summary()["simulated"],100)
            finally:
                f.close()

if __name__ == "__main__":
    unittest.main()
