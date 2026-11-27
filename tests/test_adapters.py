import unittest
from backend.adapters import CURRENCIES, simulation_adapter, SimulationWalletAdapter

class AdapterTests(unittest.TestCase):
    def test_registry(self):
        self.assertEqual(set(CURRENCIES), {"DZUV","AUZV","SEZQ","DPZE","ASVR"})

    def test_disabled_currencies(self):
        for code in ("AUZV","SEZQ","DPZE","ASVR","BTC","dzuv"):
            with self.subTest(code=code), self.assertRaises(ValueError):
                simulation_adapter(code)

    def test_address_namespace(self):
        adapter = simulation_adapter("DZUV")
        self.assertIsInstance(adapter, SimulationWalletAdapter)
        self.assertTrue(adapter.validate("sim-DZUV-abcdefgh"))
        for address in (None, 42, "sim-AUZV-abcdefgh", "sim-DZUV-short", "sim-DZUV-abcdefgh\n"):
            self.assertFalse(adapter.validate(address))

    def test_deterministic_receipt(self):
        self.assertEqual(simulation_adapter("DZUV").receipt("test"),
                         simulation_adapter("DZUV").receipt("test"))
