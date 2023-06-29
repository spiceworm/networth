#!/usr/bin/env python
import asyncio
import logging
import os

import aiohttp
import click
import yaml

from src.assets import Asset
from src.assets.bullion import BULLION
from src.assets.crypto import CRYPTO
from src.assets.fiat import FIAT
from src.assets.institution import INSTITUTIONS


logging.basicConfig(
    datefmt="%H:%M:%S",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

logging.getLogger("urllib3").setLevel(logging.WARNING)

log = logging.getLogger()
log.setLevel(logging.INFO)


async def execute(loaded_assets: dict, simulated_values: dict, discreet: bool, min_balance: float):
    Asset.SESSION = aiohttp.ClientSession()

    bullion = [CLS(loaded_assets.get("bullion", {}).get(CLS.LABEL, ())) for CLS in BULLION]
    crypto = [CLS(loaded_assets.get("crypto", {}).get(CLS.LABEL, ())) for CLS in CRYPTO]
    fiat = [CLS(loaded_assets.get("fiat", {}).get(CLS.LABEL, ())) for CLS in FIAT]
    institutions = [CLS(loaded_assets.get("institutions", {}).get(CLS.LABEL, ())) for CLS in INSTITUTIONS]

    # Fetch prices for all crypto projects in a single request and store them as a class attribute
    # on `CryptoAsset`. This method only needs to be called once to fetch all price data so break
    # after calling it on the first instance.
    for project in crypto:
        await project.fetch_prices(*[project.LABEL for project in crypto])
        break

    if crypto and simulated_values:
        for project_name, value in simulated_values.items():
            crypto[0].prices[project_name] = value

    assets = [*bullion, *crypto, *fiat, *institutions]
    total_value = 0
    for asset in assets:
        if await asset.quantity:
            total_value += await asset.value

    terminal_size = os.get_terminal_size()

    for asset_objs in (bullion, crypto, fiat, institutions):
        click.echo("-" * terminal_size.columns)

        for asset in sorted(asset_objs):
            if await asset.quantity > 0:
                value = await asset.value
                quantity = await asset.quantity
                price = await asset.price

                if value < min_balance:
                    continue

                asset_value = "X" if discreet else f"{value:<15,.2f}"
                portfolio_allocation = f"{value / total_value * 100:.4f}"
                asset_quantity = "X" if discreet else f"{quantity:,}"
                fmt_price = f'{price:,}'
                msg = (
                    f"{asset.SYMBOL:>13}: ${asset_value} ({portfolio_allocation}%) "
                    f'({asset_quantity} @ ${click.style(fmt_price, fg="cyan")})'
                )
                click.echo(msg)

    click.echo("=" * terminal_size.columns)

    fmt_total_value = "X" if discreet else f"{total_value:,.2f}"
    click.secho(f"     Networth: ${fmt_total_value}", fg="green")

    await Asset.SESSION.close()


@click.command()
@click.option("-d", "--discreet", is_flag=True)
@click.option("-m", "--min-balance", type=float, default=10.0)
@click.option("-s", "--simulate", type=str)
@click.option("-u", "--update-assets", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.option("-z", "--no-fetch", is_flag=True)
def main(discreet, min_balance, simulate, update_assets, verbose, no_fetch) -> None:
    simulated_values = {}

    if update_assets:
        click.edit(editor="vim", filename="assets.yaml")
    if no_fetch:
        return
    if verbose:
        log.setLevel(logging.DEBUG)
    if simulate:
        for pair in simulate.split(","):
            project_name, value = pair.split("=")
            simulated_values[project_name] = float(value)

    with open("assets.yaml") as f:
        assets = yaml.safe_load(f)

    asyncio.run(execute(assets, simulated_values, discreet, min_balance))


if __name__ == "__main__":
    main()
