import asyncio
import logging
import os
from typing import List, Union

import aiohttp


log = logging.getLogger(__name__)
_sem = asyncio.Semaphore()


def wei_to_ether(wei) -> float:
    return int(wei) * 10**-18


class EtherScan:
    API_URL = "https://api.etherscan.io"
    BALANCES = {}

    def __init__(self, session: aiohttp.ClientSession):
        self.api_key = os.environ["ETHERSCAN_API_KEY"]
        self.session = session

    def _build_url(self, **kwargs) -> str:
        kwargs.update({"apikey": self.api_key})
        params = "&".join(f"{k}={v}" for k, v in kwargs.items())
        return f"{self.API_URL}/api?{params}"

    async def _send(self, request, **kwargs) -> dict:
        url = self._build_url(**kwargs)
        log.debug(f"Sending request to {url}")
        async with _sem:
            await asyncio.sleep(0.2)
            async with request(url=url) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_ether_balance(self, address: str) -> float:
        return await self.get_ether_balances(address, return_sum=True)

    async def get_ether_balances(self, *addresses, return_sum: bool = False) -> Union[float, List[dict]]:
        params = {"module": "account", "action": "balancemulti", "address": ",".join(addresses)}
        retval = await self._send(self.session.get, **params)
        accounts = retval["result"]
        if not return_sum:
            for account in accounts:
                account["balance"] = wei_to_ether(account["balance"])
            return accounts
        return wei_to_ether(sum(int(acct["balance"]) for acct in accounts))

    async def get_token_balance(self, address: str, contract_address: str) -> float:
        params = {
            "action": "tokenbalance",
            "address": address,
            "contractaddress": contract_address,
            "module": "account",
            "tag": "latest",
        }
        retval = await self._send(self.session.get, **params)
        return wei_to_ether(retval["result"])
