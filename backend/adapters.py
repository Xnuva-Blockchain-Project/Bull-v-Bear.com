"""Offline wallet adapter contract. No network or signing implementation."""
from abc import ABC, abstractmethod
from types import MappingProxyType
import re

CURRENCIES = MappingProxyType({
    "DZUV": "Denzuve", "AUZV": "Aurzola", "SEZQ": "Sestovi",
    "DPZE": "Duprezo", "ASVR": "Asveru"
})

class SimulationWalletAdapter(ABC):
    @abstractmethod
    def validate(self, address):
        """Return whether a synthetic address belongs to this currency."""

    @abstractmethod
    def receipt(self, claim_id):
        """Return a deterministic synthetic receipt, never a transaction ID."""

class DenzuveSimulationWallet(SimulationWalletAdapter):
    def validate(self, address):
        return isinstance(address, str) and re.fullmatch(
            r"sim-DZUV-[a-zA-Z0-9]{8,64}", address) is not None

    def receipt(self, claim_id):
        return "simulation-" + claim_id

def simulation_adapter(currency):
    if currency != "DZUV":
        raise ValueError("currency not enabled for simulation")
    return DenzuveSimulationWallet()
