#!/usr/bin/env python
import logging
import operator
import os

import click
import yaml

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


@click.command()
@click.option('-d', '--discreet', is_flag=True)
@click.option('-u', '--update-assets', is_flag=True)
@click.option('-v', '--verbose', is_flag=True)
@click.option('-z', '--no-fetch', is_flag=True)
def main(discreet, update_assets, verbose, no_fetch):
    if update_assets:
        click.edit(editor='vim', filename='assets.yaml')
    if no_fetch:
        return
    if verbose:
        log.setLevel(logging.DEBUG)

    with open('assets.yaml') as f:
        assets = yaml.safe_load(f)

    bullion = [CLS(assets['bullion'].get(CLS.LABEL, ())) for CLS in BULLION]
    crypto = [CLS(assets['crypto'].get(CLS.LABEL, ())) for CLS in CRYPTO]
    fiat = [CLS(assets['fiat'].get(CLS.LABEL, ())) for CLS in FIAT]
    institutions = [CLS(assets['institutions'].get(CLS.LABEL, ())) for CLS in INSTITUTIONS]

    assets = [*bullion, *crypto, *fiat, *institutions]
    total_value = sum(asset.value for asset in assets)

    terminal_size = os.get_terminal_size()

    for asset_objs in (bullion, crypto, fiat, institutions):
        click.echo('-' * terminal_size.columns)

        for asset in sorted(asset_objs, key=operator.attrgetter('value')):
            if asset.value == 0:
                continue

            asset_value = 'X' if discreet else f'{asset.value:<15,.2f}'
            portfolio_allocation = f'{asset.value / total_value * 100:.4f}'
            asset_quantity = 'X' if discreet else f'{asset.quantity:,}'
            msg = (
                f'{asset.SYMBOL:>13}: ${asset_value} ({portfolio_allocation}%) '
                f'({asset_quantity} @ ${click.style(asset.price, fg="cyan")})'
            )
            click.echo(msg)

    click.echo('=' * terminal_size.columns)

    fmt_total_value = 'X' if discreet else f'{total_value:,.2f}'
    click.secho(f'     Networth: ${fmt_total_value}', fg='green')


if __name__ == '__main__':
    main()
