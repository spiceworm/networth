from typing import Iterable

import grazer

from .. import Asset


class StockAsset(Asset):
    prices = {}

    def __init__(self, quantities: Iterable[float | int] = ()):
        super().__init__(quantities)

    @property
    async def price(self) -> float:
        return StockAsset.prices[self.SYMBOL]


class STOCKS:
    @classmethod
    def from_dict(cls, d):
        for label, config in d.items():
            async def fetch_prices(slf, elements) -> None:
                if not StockAsset.prices:
                    for result in grazer.graze(elements=elements):
                        lbl, price = result.popitem()
                        StockAsset.prices[lbl] = float(price)

            _cls = type(
                label,
                (StockAsset,),
                {
                    "LABEL": label,
                    "SYMBOL": label,
                    "fetch_prices": fetch_prices,
                }
            )
            quantity = float(config["quantity"])
            yield _cls([quantity])
