import functools
import json

from .. import Asset


class BullionAsset(Asset):
    _PRICES = None

    @property
    async def price(self) -> float:
        if BullionAsset._PRICES is None:
            async with self.SESSION.get('https://api.metals.live/v1/spot') as resp:
                resp.raise_for_status()
                # Mimetype is not set in response. Manually load json to silence warning
                data = await resp.read()
                retval = json.loads(data)
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
