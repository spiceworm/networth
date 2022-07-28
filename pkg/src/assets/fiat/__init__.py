from .. import Asset


class FiatAsset(Asset):
    pass


class USD(FiatAsset):
    LABEL = "usd"
    SYMBOL = "USD"

    @property
    async def price(self) -> float:
        return 1.0


FIAT = [USD]
