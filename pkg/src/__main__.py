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


async def execute(loaded_assets: dict, discreet: bool, min_balance: float):
    Asset.SESSION = aiohttp.ClientSession()

    bullion = [CLS(loaded_assets["bullion"].get(CLS.LABEL, ())) for CLS in BULLION]
    crypto = [CLS(loaded_assets["crypto"].get(CLS.LABEL, ())) for CLS in CRYPTO]
    fiat = [CLS(loaded_assets["fiat"].get(CLS.LABEL, ())) for CLS in FIAT]
    institutions = [CLS(loaded_assets["institutions"].get(CLS.LABEL, ())) for CLS in INSTITUTIONS]

    # Fetch prices for all crypto projects in a single request and store them as a class attribute
    # on `CryptoAsset`. This method only needs to be called once to fetch all price data so break
    # after calling it on the first instance.
    for project in crypto:
        await project.fetch_prices(*[project.LABEL for project in crypto])
        break

    assets = [*bullion, *crypto, *fiat, *institutions]
    total_value = 0  # sum(await asset.value for asset in assets)
    for asset in assets:
        total_value += await asset.value

    terminal_size = os.get_terminal_size()

    for asset_objs in (bullion, crypto, fiat, institutions):
        click.echo("-" * terminal_size.columns)

        for asset in sorted(asset_objs):
            value = await asset.value
            quantity = await asset.quantity
            price = await asset.price

            if value < min_balance:
                continue

            asset_value = "X" if discreet else f"{value:<15,.2f}"
            portfolio_allocation = f"{value / total_value * 100:.4f}"
            asset_quantity = "X" if discreet else f"{quantity:,}"
            msg = (
                f"{asset.SYMBOL:>13}: ${asset_value} ({portfolio_allocation}%) "
                f'({asset_quantity} @ ${click.style(price, fg="cyan")})'
            )
            click.echo(msg)

    click.echo("=" * terminal_size.columns)

    fmt_total_value = "X" if discreet else f"{total_value:,.2f}"
    click.secho(f"     Networth: ${fmt_total_value}", fg="green")

    await Asset.SESSION.close()


@click.command()
@click.option("-d", "--discreet", is_flag=True)
@click.option("-m", "--min-balance", type=float, default=10.0)
@click.option("-u", "--update-assets", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.option("-z", "--no-fetch", is_flag=True)
def main(discreet, min_balance, update_assets, verbose, no_fetch) -> None:
    if update_assets:
        click.edit(editor="vim", filename="assets.yaml")
    if no_fetch:
        return
    if verbose:
        log.setLevel(logging.DEBUG)

    with open("assets.yaml") as f:
        assets = yaml.safe_load(f)

    asyncio.run(execute(assets, discreet, min_balance))


if __name__ == "__main__":
    main()
