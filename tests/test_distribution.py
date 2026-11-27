import unittest
from backend.distribution import DistributionPolicy

class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.p = DistributionPolicy(20,4,100000000,500000000)

    def quote(self, **kwargs):
        inputs = dict(now=100000,available=100000000000,pending=0,paid=[],healthy=True)
        inputs.update(kwargs)
        return self.p.quote(**inputs)

    def test_supply_scaling(self):
        self.assertEqual(self.p.daily_ceiling,500000000)
        self.assertEqual(DistributionPolicy(20,4,100000000,100).daily_ceiling,100)

    def test_fractional_treasury(self):
        self.assertEqual(self.quote(available=100000000),100000)

    def test_pending_never_expires(self):
        self.assertEqual(self.quote(pending=500000000),0)

    def test_rolling_boundary(self):
        self.assertEqual(self.quote(paid=[(13601,500000000)]),0)
        self.assertGreater(self.quote(paid=[(13600,500000000)]),0)

    def test_remaining_budget(self):
        self.assertEqual(self.quote(pending=499999999),1)

    def test_health(self):
        self.assertEqual(self.quote(healthy=False),0)

    def test_invalid_time_and_market(self):
        with self.assertRaises(ValueError):
            self.quote(paid=[(100001,1)])
        with self.assertRaises(ValueError):
            DistributionPolicy(20,4,100000000,500000000,1)
