from typing import Iterable

from .. import Asset


class VehicleAsset(Asset):
    def __init__(self, quantities: Iterable[float | int] = ()):
        super().__init__(quantities)
        self._price = 1.0

    @property
    async def price(self) -> float:
        return self._price


class Automobiles(VehicleAsset):
    LABEL = "automobiles"
    SYMBOL = "Automobiles"


VEHICLES = [Automobiles]
