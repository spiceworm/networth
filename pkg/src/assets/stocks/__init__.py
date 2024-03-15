import logging
import os
from typing import Iterable

import finnhub

from .. import Asset


log = logging.getLogger()


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
            async def fetch_prices(slf, elements: dict) -> None:
                if not StockAsset.prices:
                    client = finnhub.Client(api_key=os.environ["FINNHUB_API_KEY"])
                    for symbol, meta in elements.items():
                        if "value" in meta:
                            log.debug("Using hardcoded price of %s for %s", meta["value"], symbol)
                            StockAsset.prices[symbol] = float(meta["value"])
                        else:
                            log.debug("Fetching price for %s", symbol)
                            resp = client.quote(symbol)
                            StockAsset.prices[symbol] = float(resp["c"])

            _cls = type(
                label,
                (StockAsset,),
                {
                    "LABEL": label,
                    "SYMBOL": label,
                    "fetch_prices": fetch_prices,
                }
            )
            yield _cls([float(qty) for qty in config["quantity"]])
