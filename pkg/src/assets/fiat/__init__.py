from .. import Asset


class FiatAsset(Asset):
    pass


class USD(FiatAsset):
    LABEL = 'usd'
    SYMBOL = 'USD'

    @property
    def price(self):
        return 1


FIAT = [USD]
