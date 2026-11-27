import unittest
from backend.supply_reference import simulation_policy, PROVISIONAL_SUPPLIES

class SupplyReferenceTests(unittest.TestCase):
    def test_exact_reference_limits(self):
        expected = {"AUZV":100000000,"DZUV":500000000,"SEZQ":952380952,
                    "DPZE":1190476190,"ASVR":2619047619}
        for code, ceiling in expected.items():
            with self.subTest(code=code):
                p = simulation_policy(code,100000000)
                self.assertEqual(p.daily_ceiling,ceiling)
                self.assertEqual(p.market_weight,0)

    def test_explicit_precision(self):
        self.assertEqual(simulation_policy("DZUV",100).daily_ceiling,500)
        for precision in (0,-1,True,1.5):
            with self.assertRaises(ValueError):
                simulation_policy("DZUV",precision)

    def test_unknown_currency(self):
        with self.assertRaises(ValueError):
            simulation_policy("BTC",100000000)

    def test_reference_immutable(self):
        with self.assertRaises(TypeError):
            PROVISIONAL_SUPPLIES["DZUV"] = 1
