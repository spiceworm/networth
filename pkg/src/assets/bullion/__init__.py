import functools
import json
import logging
from typing import Dict

from .. import Asset


log = logging.getLogger(__name__)


class BullionAsset(Asset):
    _PRICES: Dict[str, str] | None = None

    @property
    async def price(self) -> float:
        if BullionAsset._PRICES is None:
            url = "https://api.metals.live/v1/spot"
            log.debug(f"Sending request to {url}")
            async with self.SESSION.get(url, raise_for_status=True) as resp:
                # Mimetype is not set in response. Manually load json to silence warning
                data = await resp.read()
                retval = json.loads(data)
            merge_dicts = lambda a, b: {**a, **b}
            BullionAsset._PRICES = functools.reduce(merge_dicts, retval)
        return float(BullionAsset._PRICES[self.LABEL])


class Gold(BullionAsset):
    LABEL = "gold"
    SYMBOL = "GLD"


class Silver(BullionAsset):
    LABEL = "silver"
    SYMBOL = "SLV"


BULLION = [Gold, Silver]
