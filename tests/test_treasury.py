import unittest
from backend.treasury import TreasurySnapshot, quotes

class TreasuryTests(unittest.TestCase):
    def test_exclusions(self):
        s = TreasurySnapshot("DZUV",1000,immature=9000,orphaned=5000,queued=200,fees=100,reserve=200,healthy=True)
        self.assertEqual(s.available,500)
        self.assertEqual(s.quote(1,100,10),50)

    def test_shortfall(self):
        s = TreasurySnapshot("DZUV",100,queued=200,healthy=True)
        self.assertEqual(s.available,0)
        self.assertEqual(s.quote(1,100),0)

    def test_health_and_recovery(self):
        self.assertEqual(TreasurySnapshot("DZUV",1000).quote(1,100),0)
        self.assertEqual(TreasurySnapshot("DZUV",1000,healthy=True).quote(1,100),10)

    def test_cap_and_minimum(self):
        self.assertEqual(TreasurySnapshot("DZUV",100000,healthy=True).quote(1,20),20)
        self.assertEqual(TreasurySnapshot("DZUV",100,healthy=True).quote(2,20),0)

    def test_currency_isolation(self):
        self.assertEqual(quotes([TreasurySnapshot("DZUV",100,healthy=True),TreasurySnapshot("AUZV",100000,healthy=True)],2,20),{"DZUV":0,"AUZV":0})

    def test_invalid_inputs(self):
        for amount in (-1,True,1.5,10**16):
            with self.assertRaises(ValueError):
                TreasurySnapshot("DZUV",amount)
        with self.assertRaises(ValueError):
            TreasurySnapshot("UNKNOWN",0)
        with self.assertRaises(ValueError):
            TreasurySnapshot("DZUV",100).quote(2,1)

    def test_duplicate_snapshot(self):
        s = TreasurySnapshot("DZUV",100)
        with self.assertRaises(ValueError):
            quotes([s,s],1,20)
