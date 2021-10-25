class Asset:
    SYMBOL = None
    LABEL = None

    def __init__(self, quantities=()):
        self._quantity = sum(quantities)
        self._price = None

    @property
    def price(self):
        raise NotImplemented

    @property
    def quantity(self):
        return self._quantity

    @property
    def value(self):
        return float(self.price) * self.quantity
