import base64
import hashlib
import hmac
import json
import logging
import os
import time
from typing import Dict, Iterable

import aiohttp


log = logging.getLogger(__name__)


class Gemini:
    API_URL: str = "https://api.gemini.com"
    BALANCES: Iterable[Dict[str, str]] | None = None
    EARN_BALANCES: Iterable[Dict[str, str]] | None = None

    def __init__(self, session: aiohttp.ClientSession = None):
        self.api_key = os.environ["GEMINI_API_KEY"]
        self.api_secret = os.environ["GEMINI_API_SECRET"].encode()
        self.session = session

    async def _auth_send(self, **payload) -> Dict:
        payload["nonce"] = time.time()
        encoded_payload = json.dumps(payload).encode()
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(self.api_secret, b64, hashlib.sha384).hexdigest()

        endpoint = payload["request"]
        url = self._get_url(endpoint)
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self.api_key,
            "X-GEMINI-PAYLOAD": b64.decode(),
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache",
        }

        log.debug(f"Sending request to {url}")
        async with self.session.post(
                url=url,
                json=payload,
                headers=headers,
                raise_for_status=True,
        ) as resp:
            return await resp.json()

    def _get_url(self, endpoint) -> str:
        return self.API_URL + endpoint

    async def get_balance(self, symbol) -> float:
        return await self._get_trading_balance(symbol) + await self._get_earn_balance(symbol)

    async def _get_earn_balance(self, symbol) -> float:
        for earn_account in await self._get_earn_balances():
            if earn_account["currency"] == symbol:
                return float(earn_account["balance"])
        return 0.0

    async def _get_earn_balances(self) -> Iterable[Dict[str, str]]:
        if Gemini.EARN_BALANCES is None:
            Gemini.EARN_BALANCES = await self._auth_send(request="/v1/balances/earn")
        return Gemini.EARN_BALANCES

    async def _get_trading_balance(self, symbol) -> float:
        for account in await self._get_trading_balances():
            if account["currency"] == symbol:
                return float(account["amount"])
        return 0.0

    async def _get_trading_balances(self) -> Iterable[Dict[str, str]]:
        if Gemini.BALANCES is None:
            Gemini.BALANCES = await self._auth_send(request="/v1/balances")
        return Gemini.BALANCES
