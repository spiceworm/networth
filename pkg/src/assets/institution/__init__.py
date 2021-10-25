from .. import Asset


class InstitutionalAsset(Asset):
    @property
    def price(self):
        if self._price is None:
            self._price = 1
        return self._price


class Fidelity(InstitutionalAsset):
    LABEL = 'fidelity'
    SYMBOL = 'Fidelity'


class MerrillLynch(InstitutionalAsset):
    LABEL = 'merrill-lynch'
    SYMBOL = 'Merrill Lynch'


class UMCU(InstitutionalAsset):
    LABEL = 'umcu'
    SYMBOL = 'UMCU'


INSTITUTIONS = [Fidelity, MerrillLynch, UMCU]
