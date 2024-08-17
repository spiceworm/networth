#!/usr/bin/env python
import asyncio
import itertools
import logging
import os

import click
import yaml

from src.assets import (
    Asset,
    AssetDetail,
)


logging.basicConfig(
    datefmt="%H:%M:%S",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

logging.getLogger("urllib3").setLevel(logging.WARNING)
log = logging.getLogger()


async def execute(loaded_assets: dict, verbose: bool):
    asset_objs = []
    indent = 0
    for name, asset_meta in loaded_assets.items():
        if len(name) > indent:
            indent = len(name)

        group = asset_meta["group"]
        sources = asset_meta["sources"]
        category = asset_meta["category"]

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
    for asset in asset_objs:
        total_value += await asset.value()

    terminal_size = os.get_terminal_size()

    objects = sorted(asset_objs, key=lambda o: o.group)
    for group, objs in itertools.groupby(objects, lambda o: o.group):
        click.echo("-" * terminal_size.columns)

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
            fmt_price = f"{await detail.price():,}"
            portfolio_allocation = (await detail.value() / total_value) * 100
            group_allocation_sum += portfolio_allocation
            msg = (
                f"{name:>{indent}}: ${await detail.value():<{indent},.2f} ({portfolio_allocation:.4f}%) "
                f'({await detail.quantity():,} @ ${click.style(fmt_price, fg="cyan")}) [{detail.assets[0].category}]'
            )
            click.echo(msg)

            if verbose:
                for asset in detail.assets:
                    click.echo(" " * indent + f"- {asset.source}: {await asset.quantity()}")

        group_value_sum = f"{group_value_sum:<{indent},.2f}"
        click.echo(f"{'':>{indent}}: ${click.style(group_value_sum, fg='blue')} ({group_allocation_sum:.4f}%)")

    click.echo("=" * terminal_size.columns)
    click.secho(f"{'Networth':>{indent}}: ${total_value:,.2f}", fg="green")


@click.command()
@click.option("-e", "--edit-assets", is_flag=True)
@click.option("-d", "--debug", is_flag=True)
@click.option("-f", "--file", default="assets.yaml")
@click.option("-v", "--verbose", is_flag=True)
def main(edit_assets, debug, file, verbose) -> None:
    if edit_assets:
        click.edit(editor="vim", filename=file)

    if debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    with open(file) as f:
        assets = yaml.safe_load(f)

    asyncio.run(execute(assets, verbose))


if __name__ == "__main__":
    main()
