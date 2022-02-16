class Asset:
    SYMBOL = None
    LABEL = None

    def __init__(self, quantities=()):
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
