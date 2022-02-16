import functools

import requests

from .. import Asset


class BullionAsset(Asset):
    _PRICES = None

    @property
    def price(self) -> float:
        if BullionAsset._PRICES is None:
            resp = requests.get('https://api.metals.live/v1/spot')
            resp.raise_for_status()
            retval = resp.json()
            merge_dicts = lambda a, b: {**a, **b}
            BullionAsset._PRICES = functools.reduce(merge_dicts, retval)
        return BullionAsset._PRICES[self.LABEL]


class Gold(BullionAsset):
    LABEL = 'gold'
    SYMBOL = 'GLD'


class Silver(BullionAsset):
    LABEL = 'silver'
    SYMBOL = 'SLV'


BULLION = [Gold, Silver]
