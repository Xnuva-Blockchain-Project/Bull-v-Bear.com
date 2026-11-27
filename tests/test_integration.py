import unittest
from backend.faucet import Faucet

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.f = Faucet()
        self.f.fund(1000)
        self.addCleanup(self.f.close)

    def test_default_closed(self):
        with self.assertRaises(ValueError):
            self.f.claim("DZUV","sim-DZUV-abcdefgh",100000)

    def test_dynamic_quote_reserves(self):
        self.f.configure_simulation(healthy=True,reserve=200,fees=100,divisor=10)
        c = self.f.claim("DZUV","sim-DZUV-abcdefgh",100000)
        self.assertEqual(self.f.summary(),{"available":630,"queued":70,"simulated":0})
        self.f.process(c)
        self.assertEqual(self.f.summary(),{"available":630,"queued":0,"simulated":70})

    def test_pause_resume_queue(self):
        self.f.configure_simulation(healthy=True)
        c = self.f.claim("DZUV","sim-DZUV-abcdefgh",100000)
        self.f.configure_simulation(healthy=False)
        with self.assertRaises(ValueError):
            self.f.process(c)
        self.assertEqual(self.f.summary()["queued"],10)
        self.f.configure_simulation(healthy=True)
        self.assertEqual(self.f.process(c),self.f.process(c))

    def test_reserve_shortfall_blocks_payment(self):
        self.f.configure_simulation(healthy=True)
        c = self.f.claim("DZUV","sim-DZUV-abcdefgh",100000)
        self.f.configure_simulation(healthy=True,reserve=1000)
        with self.assertRaises(ValueError):
            self.f.process(c)
        self.assertEqual(self.f.summary()["queued"],10)

    def test_replenishment(self):
        self.f.configure_simulation(healthy=True,reserve=1000)
        with self.assertRaises(ValueError):
            self.f.claim("DZUV","sim-DZUV-abcdefgh",100000)
        self.f.fund(100)
        self.f.claim("DZUV","sim-DZUV-abcdefgh",100000)
        self.assertEqual(self.f.summary()["queued"],1)
