#!/usr/bin/env python
import asyncio
import functools
import itertools
import logging
import os
from typing import Tuple

import aioetherscan
import aiohttp
import click
import decouple
import pycoingecko
import yaml


logging.basicConfig(
    datefmt="%H:%M:%S",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

logging.getLogger("urllib3").setLevel(logging.WARNING)
log = logging.getLogger()


ETHERSCAN_API_KEY = decouple.config("ETHERSCAN_API_KEY")
FINNHUB_API_KEY = decouple.config("FINNHUB_API_KEY")


@functools.total_ordering
class AssetBase:
    def __init__(self, name, group, source, quantity, price):
        self.name = name
        self.group = group
        self.source = source
        self._quantity = quantity
        self._price = float(price)
        self._value = 0.0

    def __eq__(self, other) -> bool:
        return self._value == other._value

    def __lt__(self, other) -> bool:
        return self._value < other._value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name=}, {self.group=}, {self.source=}, {self._quantity=}, {self._price=})"

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
    COLOR = "bright_green"


class Crypto(AssetBase):
    COLOR = "bright_yellow"
    PRICES = {}

    def __init__(self, name, group, source, quantity_or_address, price):
        super().__init__(name, group, source, quantity_or_address, price)

        if self._price:
            Crypto.PRICES[self.name] = self._price

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
            client = aioetherscan.Client(ETHERSCAN_API_KEY)
            try:
                log.debug("Etherscan API GET -> %s", self.address)
                balance = await client.account.balance(self.address)
                log.debug("Etherscan API GET <- %s", balance)
                self._quantity = int(balance) * 10**-18
            finally:
                await client.close()
        return await super().quantity()


class Stock(AssetBase):
    COLOR = "bright_cyan"
    PRICES = {}

    def __init__(self, name, group, source, quantity, price):
        super().__init__(name, group, source, quantity, price)

        if self._price:
            Stock.PRICES[self.name] = self._price

    async def price(self):
        if self.name in Stock.PRICES:
            return Stock.PRICES[self.name]
        base_url = "https://api.finnhub.io/api/v1"
        headers = {
            "Accept": "application/json",
            "User-Agent": "finnhub/python",
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            params = {"symbol": self.name, "token": FINNHUB_API_KEY}
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

    def fmt_name(self, indent) -> str:
        return click.style(self.name.rjust(indent), fg=self.assets[0].COLOR, reverse=True)

    async def fmt_price(self) -> str:
        return click.style(f"${await self.price():,}", fg="bright_blue", bold=True)

    async def fmt_quantity(self) -> str:
        return f"{await self.quantity():,}"

    async def fmt_value(self, indent) -> str:
        return f"${await self.value():<{indent},.2f}"

    async def price(self):
        return await self.assets[0].price()

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


def get_color_for_sum(value: float) -> str:
    if value > 0.0:
        return "bright_green"
    elif value < 0.0:
        return "red"
    else:
        return "white"


async def execute(loaded_assets: dict, debug: bool, excluded_groups: Tuple[str], group_by: str, verbose: bool):
    asset_objs = []
    indent = 0
    for name, asset_meta in loaded_assets.items():
        if len(name) > indent:
            indent = len(name)

        group = asset_meta["group"]
        sources = asset_meta["sources"]
        category = asset_meta["category"]

        if group in excluded_groups:
            continue

        if isinstance(category, dict):
            category_name = category["name"]
            price = category["price"]
        else:
            category_name = category
            price = 0.0

        for source, quantity_or_locator in sources.items():
            asset = Asset.create(
                category=category_name,
                name=name,
                group=group,
                source=source,
                quantity_or_locator=quantity_or_locator,
                price=price,
            )
            asset_objs.append(asset)

    total_value = 0.0

    if debug:
        for asset in asset_objs:
            total_value += await asset.value()
    else:
        with click.progressbar(asset_objs) as progress_bar:
            for asset in progress_bar:
                total_value += await asset.value()

    terminal_size = os.get_terminal_size()

    objects = sorted(asset_objs, key=lambda o: getattr(o, group_by))
    for group, objs in itertools.groupby(objects, lambda o: getattr(o, group_by)):
        group_banner_margin = int((terminal_size.columns - len(group)) / 2)
        click.echo(f'{"-" * group_banner_margin}{group}{"-" * group_banner_margin}')

        group_value_sum = 0.0
        asset_details = {}
        for name, assets in itertools.groupby(objs, lambda o: o.name):
            detail = AssetDetail(assets)
            group_value_sum += await detail.value()
            asset_details[name] = {
                "detail": detail,
                "value": await detail.value(),
            }

        group_allocation_sum = 0.0
        for name, details in sorted(asset_details.items(), key=lambda o: o[1]["value"]):
            detail = details["detail"]
            portfolio_allocation = (await detail.value() / total_value) * 100
            group_allocation_sum += portfolio_allocation
            msg = (
                f"{detail.fmt_name(indent)}: {await detail.fmt_value(indent)} ({portfolio_allocation:.4f}%) "
                f"({await detail.fmt_quantity()} @ {await detail.fmt_price()})"
            )
            click.echo(msg)

            if verbose:
                for asset in detail.assets:
                    click.echo(f"{'':>{indent}}- {asset.source}: {await asset.quantity()}")

        group_value_sum_str = f"{group_value_sum:<{indent},.2f}"
        click.echo(f"{'':>{indent}}: ${click.style(group_value_sum_str, fg=get_color_for_sum(group_value_sum))} ({group_allocation_sum:.4f}%)")

    click.echo("=" * terminal_size.columns)
    click.secho(f"{'Networth':>{indent}}: ${total_value:,.2f}", fg=get_color_for_sum(total_value), bold=True)


class DynamicGroupChoice(click.ParamType):
    name = "group"
    available_groups = set()

    def __init__(self, assets_path: str):
        try:
            with open(assets_path) as f:
                assets = yaml.safe_load(f)
        except Exception:
            # Failed to load groups for help - will validate at runtime
            pass
        else:
            self.available_groups = sorted({asset_meta["group"] for asset_meta in assets.values()})

    def convert(self, value, param, ctx):
        if value not in self.available_groups:
            self.fail(f"Invalid group: {value}. Available groups: {', '.join(sorted(self.available_groups))}", param, ctx)
        else:
            return value

    def get_metavar(self, param, ctx):
        return f"[{', '.join(self.available_groups)}]" if self.available_groups else "GROUP"


@click.command(context_settings={"show_default": True})
@click.option("-d", "--debug", is_flag=True, help="Enable debug mode.")
@click.option("-e", "--edit-assets", is_flag=True, help="Edit the assets YAML file.")
@click.option(
    "-X",
    "--exclude-group",
    "excluded_groups",
    multiple=True,
    type=DynamicGroupChoice("assets.yaml"),
    help="Exclude group from output.",
)
@click.option("-f", "--assets-file", default="assets.yaml", is_eager=True, type=click.File(), help="Path to the assets YAML file.")
@click.option("-g", "--group-by", default="group", type=click.Choice(["category", "group"]), help="Group by category or group.")
@click.option("-v", "--verbose", is_flag=True, help="Show detailed breakdown of each asset.")
def main(debug, edit_assets, excluded_groups, assets_file, group_by, verbose) -> None:
    if edit_assets:
        click.edit(editor="vim", filename=assets_file.name)

    if debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    assets = yaml.safe_load(assets_file)
    asyncio.run(execute(assets, debug, excluded_groups, group_by, verbose))


if __name__ == "__main__":
    main()
