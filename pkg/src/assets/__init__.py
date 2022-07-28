from __future__ import annotations

import functools
import logging
from typing import Iterable, Union


log = logging.getLogger()


@functools.total_ordering
class Asset:
    SESSION = None
    SYMBOL = None
    LABEL = None

    def __init__(self, quantities: Iterable[Union[float, int]] = ()):
        if quantities:
            log.debug("Hardcoded quantities for %s:", self.__class__.__name__)
            for qty in quantities:
                log.debug("- %s", qty)

        self._quantity = sum(quantities)
        self._price = None
        self._value = None

    def __eq__(self, other: Asset) -> bool:
        return (self._value or 0) == (other._value or 0)

    def __lt__(self, other: Asset) -> bool:
        return (self._value or 0) < (other._value or 0)

    @property
    async def price(self) -> float:
        raise NotImplemented

    @property
    async def quantity(self) -> float:
        return self._quantity

    @property
    async def value(self) -> float:
        if self._value is None:
            self._value = float(await self.price) * await self.quantity
        return self._value
