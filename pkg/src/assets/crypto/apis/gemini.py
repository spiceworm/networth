import base64
from datetime import datetime
import hashlib
import hmac
import json
import os
import time
from typing import Union

import requests


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

    def __init__(self):
        self.api_key = os.environ['GEMINI_API_KEY']
        self.api_secret = os.environ['GEMINI_API_SECRET'].encode()

    def _auth_send(self, **payload) -> dict:
        t = datetime.now()
        payload['nonce'] = str(int(time.mktime(t.timetuple()) * 1000) + next(COUNTER))
        encoded_payload = json.dumps(payload).encode()
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(self.api_secret, b64, hashlib.sha384).hexdigest()
        return self._send(
            request=requests.post,
            endpoint=payload['request'],
            headers={
                'Content-Type': 'text/plain',
                'Content-Length': '0',
                'X-GEMINI-APIKEY': self.api_key,
                'X-GEMINI-PAYLOAD': b64,
                'X-GEMINI-SIGNATURE': signature,
                'Cache-Control': 'no-cache'
            }
        )

    def _get_url(self, endpoint) -> str:
        return self.API_URL + endpoint

    def _send(self, request, endpoint, headers=None, payload=None) -> dict:
        resp = request(
            url=self._get_url(endpoint),
            json=payload or {},
            headers=headers or {}
        )
        resp.raise_for_status()
        return resp.json()

    def get_balance(self, symbol) -> Union[float, int]:
        return self._get_trading_balance(symbol) + self._get_earn_balance(symbol)

    def _get_earn_balance(self, symbol) -> Union[float, int]:
        for earn_account in self._get_earn_balances():
            if earn_account['currency'] == symbol:
                return float(earn_account['balance'])
        return 0

    def _get_earn_balances(self) -> dict:
        if Gemini.EARN_BALANCES is None:
            Gemini.EARN_BALANCES = self._auth_send(request='/v1/balances/earn')
        return Gemini.EARN_BALANCES

    def _get_trading_balance(self, symbol) -> Union[float, int]:
        for account in self._get_trading_balances():
            if account['currency'] == symbol:
                return float(account['amount'])
        return 0

    def _get_trading_balances(self) -> dict:
        if Gemini.BALANCES is None:
            Gemini.BALANCES = self._auth_send(request='/v1/balances')
        return Gemini.BALANCES
