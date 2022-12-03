from typing import Iterable

from .. import Asset


class InstitutionalAsset(Asset):
    def __init__(self, quantities: Iterable[float | int] = ()):
        super().__init__(quantities)
        self._price = 1.0

    @property
    async def price(self) -> float:
        return self._price


class CharlesSchwab(InstitutionalAsset):
    LABEL = "charles-schwab"
    SYMBOL = "Charles Schwab"


class Fidelity(InstitutionalAsset):
    LABEL = "fidelity"
    SYMBOL = "Fidelity"


class IBonds(InstitutionalAsset):
    LABEL = "ibonds"
    SYMBOL = "I-Bonds"


class MerrillLynch(InstitutionalAsset):
    LABEL = "merrill-lynch"
    SYMBOL = "Merrill Lynch"


class RealEstate(InstitutionalAsset):
    LABEL = "real-estate"
    SYMBOL = "Real Estate"


class UMCU(InstitutionalAsset):
    LABEL = "umcu"
    SYMBOL = "UMCU"


INSTITUTIONS = [Fidelity, CharlesSchwab, IBonds, MerrillLynch, RealEstate, UMCU]
