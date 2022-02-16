from .. import Asset


class InstitutionalAsset(Asset):
    def __init__(self, quantities):
        super().__init__(quantities)
        self._price = 1

    @property
    def price(self):
        return self._price


class Fidelity(InstitutionalAsset):
    LABEL = 'fidelity'
    SYMBOL = 'Fidelity'


class MerrillLynch(InstitutionalAsset):
    LABEL = 'merrill-lynch'
    SYMBOL = 'Merrill Lynch'


class RealEstate(InstitutionalAsset):
    LABEL = 'real-estate'
    SYMBOL = 'Real Estate'


class UMCU(InstitutionalAsset):
    LABEL = 'umcu'
    SYMBOL = 'UMCU'


INSTITUTIONS = [Fidelity, MerrillLynch, RealEstate, UMCU]
