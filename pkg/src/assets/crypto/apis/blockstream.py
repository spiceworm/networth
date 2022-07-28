import logging
from typing import List, Union

import aiohttp


log = logging.getLogger(__name__)


def satoshis_to_bitcoin(satoshis) -> float:
    return satoshis * 0.00000001


class BlockStream:
    API_URL = "https://blockstream.info"

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    def _build_url(self, **kwargs) -> str:
        endpoint = kwargs["endpoint"]
        return f"{self.API_URL}/api/{endpoint}"

    async def _send(self, request, **kwargs) -> dict:
        url = self._build_url(**kwargs)
        log.debug(f"Sending request to {url}")

        async with request(url=self._build_url(**kwargs)) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_balance(self, address: str) -> float:
        return await self.get_balances(address, return_sum=True)

    async def get_balances(self, *addresses, return_sum: bool = False) -> Union[float, List[dict]]:
        accounts = []

        # API does not support lookup for multiple addresses in a single request
        for address in addresses:
            params = {"endpoint": f"address/{address}"}
            retval = await self._send(self.session.get, **params)
            chain_stats = retval["chain_stats"]
            unspent_satoshis = chain_stats["funded_txo_sum"] - chain_stats["spent_txo_sum"]
            accounts.append(
                {
                    "address": address,
                    "balance": satoshis_to_bitcoin(unspent_satoshis),
                }
            )

        if not return_sum:
            return accounts
        return sum(account["balance"] for account in accounts)
