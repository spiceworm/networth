import functools
import logging
import os

import aioetherscan
import aiohttp
import pycoingecko


log = logging.getLogger()


@functools.total_ordering
class AssetBase:
    def __init__(self, name, group, source, quantity, price):
        self.name = name
        self.group = group
        self.source = source
        self._quantity = quantity
        self._price = price
        self._value = 0.0

    def __eq__(self, other) -> bool:
        return self._value == other._value

    def __lt__(self, other) -> bool:
        return self._value < other._value

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.name=}, {self.group=}, {self.source=}, {self._quantity=}, {self._price=})"
        )

    async def price(self) -> float:
        return float(self._price)

    @property
    def category(self):
        return self.__class__.__name__.lower()

    async def quantity(self) -> float:
        return float(self._quantity)

    async def value(self) -> float:
        self._value = float(await self.price()) * float(await self.quantity())
        return self._value


class Constant(AssetBase):
    pass


class Crypto(AssetBase):
    PRICES = {}

    def __init__(self, name, group, source, quantity_or_address, price):
        super().__init__(name, group, source, quantity_or_address, price)

        if isinstance(quantity_or_address, str):
            self.address = quantity_or_address
            self._quantity = 0.0
        else:
            self.address = None
            self._quantity = quantity_or_address

    def __repr__(self):
        if self.address is None:
            return super().__repr__()
        return f"{self.__class__.__name__}({self.name=}, {self.group=}, {self.source=}, {self.address=:.6}...)"

    async def price(self):
        if self.name in Crypto.PRICES:
            return Crypto.PRICES[self.name]
        client = pycoingecko.CoinGeckoAPI()
        log.debug("Coingecko API GET -> %s", self.name)
        retval = client.get_price(self.name, vs_currencies="usd")
        log.debug("Coingecko API GET <- %s", retval)
        self._price = float(retval[self.name]["usd"])
        Crypto.PRICES[self.name] = self._price
        return await super().price()

    async def quantity(self):
        if self.address and not self._quantity:
            api_key = os.getenv("ETHERSCAN_API_KEY")
            client = aioetherscan.Client(api_key)
            try:
                log.debug("Etherscan API GET -> %s", self.address)
                balance = await client.account.balance(self.address)
                log.debug("Etherscan API GET <- %s", balance)
                self._quantity = int(balance) * 10**-18
            finally:
                await client.close()
        return await super().quantity()


class Stock(AssetBase):
    PRICES = {}

    async def price(self):
        if self.name in Stock.PRICES:
            return Stock.PRICES[self.name]
        api_key = os.getenv("FINNHUB_API_KEY")
        base_url = "https://api.finnhub.io/api/v1"
        headers = {
            "Accept": "application/json",
            "User-Agent": "finnhub/python",
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            params = {"symbol": self.name, "token": api_key}
            log.debug("Finnhub API -> %s", self.name)
            async with session.get(f"{base_url}/quote", params=params) as resp:
                try:
                    jsn = await resp.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    log.exception(f"Error: {await resp.text()}")
                else:
                    log.debug("Finnhub API <- %s", jsn)
                    self._price = float(jsn["c"])
                    Stock.PRICES[self.name] = self._price
        return await super().price()


class Asset:
    @classmethod
    def create(cls, category, name, group, source, quantity_or_locator, price):
        match category:
            case "cryptocurrency":
                obj = Crypto(name, group, source, quantity_or_locator, price)
            case "constant":
                obj = Constant(name, group, source, quantity_or_locator, price)
            case "stock":
                obj = Stock(name, group, source, quantity_or_locator, price)
            case _:
                raise ValueError(f"Unknown asset category {category}")

        return obj


class AssetDetail:
    def __init__(self, assets):
        self.assets = list(assets)
        self.name = self.assets[0].name

    async def price(self):
        for asset in self.assets:
            return await asset.price()

    async def quantity(self):
        total = 0.0
        for asset in self.assets:
            total += await asset.quantity()
        return total

    async def value(self):
        total = 0.0
        for asset in self.assets:
            total += await asset.value()
        return total
