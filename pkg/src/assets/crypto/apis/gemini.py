import base64
from datetime import datetime
import hashlib
import hmac
import json
import logging
import os
import time
from typing import Union

import aiohttp


log = logging.getLogger(__name__)


def _counter():
    n = 1
    while True:
        yield n
        n += 1


COUNTER = _counter()


class Gemini:
    API_URL = 'https://api.gemini.com'
    BALANCES = None
    EARN_BALANCES = None

    def __init__(self, session: aiohttp.ClientSession = None):
        self.api_key = os.environ['GEMINI_API_KEY']
        self.api_secret = os.environ['GEMINI_API_SECRET'].encode()
        self.session = session

    async def _auth_send(self, **payload) -> dict:
        t = datetime.now()
        payload['nonce'] = str(int(time.mktime(t.timetuple()) * 1000) + next(COUNTER))
        encoded_payload = json.dumps(payload).encode()
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(self.api_secret, b64, hashlib.sha384).hexdigest()

        endpoint = payload['request']
        url = self._get_url(endpoint)
        headers = {
            'Content-Type': 'text/plain',
            'Content-Length': '0',
            'X-GEMINI-APIKEY': self.api_key,
            'X-GEMINI-PAYLOAD': b64.decode(),
            'X-GEMINI-SIGNATURE': signature,
            'Cache-Control': 'no-cache'
        }

        log.debug(f'Sending request to {url}')
        async with self.session.post(url=url, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    def _get_url(self, endpoint) -> str:
        return self.API_URL + endpoint

    async def get_balance(self, symbol) -> Union[float, int]:
        return await self._get_trading_balance(symbol) + await self._get_earn_balance(symbol)

    async def _get_earn_balance(self, symbol) -> Union[float, int]:
        for earn_account in await self._get_earn_balances():
            if earn_account['currency'] == symbol:
                return float(earn_account['balance'])
        return 0

    async def _get_earn_balances(self) -> dict:
        if Gemini.EARN_BALANCES is None:
            Gemini.EARN_BALANCES = await self._auth_send(request='/v1/balances/earn')
        return Gemini.EARN_BALANCES

    async def _get_trading_balance(self, symbol) -> Union[float, int]:
        for account in await self._get_trading_balances():
            if account['currency'] == symbol:
                return float(account['amount'])
        return 0

    async def _get_trading_balances(self) -> dict:
        if Gemini.BALANCES is None:
            Gemini.BALANCES = await self._auth_send(request='/v1/balances')
        return Gemini.BALANCES
