import logging


log = logging.getLogger()


class Asset:
    SYMBOL = None
    LABEL = None

    def __init__(self, quantities=()):
        if quantities:
            log.debug('Hardcoded quantities for %s:', self.__class__.__name__)
            for qty in quantities:
                log.debug('- %s', qty)

        self._quantity = sum(quantities)
        self._price = None
        self._value = None

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
