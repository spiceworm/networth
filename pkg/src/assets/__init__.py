from __future__ import annotations

import functools
import logging
from typing import List


log = logging.getLogger()


@functools.total_ordering
class Asset:
    SYMBOL = None
    LABEL = None

    def __init__(self, quantities: List[float, int] = ()):
        if quantities:
            log.debug('Hardcoded quantities for %s:', self.__class__.__name__)
            for qty in quantities:
                log.debug('- %s', qty)

        self._quantity = sum(quantities)
        self._price = None
        self._value = None

    def __eq__(self, other: Asset) -> bool:
        return self.value == other.value

    def __lt__(self, other: Asset) -> bool:
        return self.value < other.value

    @property
    def price(self):
        raise NotImplemented

    @property
    def quantity(self):
        return self._quantity

    @property
    def value(self):
        if self._value is None:
            self._value = float(self.price) * self.quantity
        return self._value
