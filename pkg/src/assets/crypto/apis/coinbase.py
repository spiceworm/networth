from datetime import datetime
import hashlib
import hmac
import logging
import os
import time
from typing import Dict

import requests
from requests.auth import AuthBase


log = logging.getLogger(__name__)


class _CoinbaseWalletAuth(AuthBase):
    def __init__(self, api_key: str, secret_key: str):
        self.api_key: str = api_key
        self.secret_key: str = secret_key

    def __call__(self, request) -> requests.Response:
        timestamp = int(time.time())
        message = f'{timestamp}{request.method}{request.path_url}{request.body or ""}'
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
        request.headers.update(
            {
                "CB-ACCESS-SIGN": signature,
                "CB-ACCESS-TIMESTAMP": timestamp,
                "CB-ACCESS-KEY": self.api_key,
                "CB-VERSION": datetime.today().strftime("%Y-%m-%d"),
            }
        )
        return request


class Coinbase:
    API_URL: str = "https://api.coinbase.com"
    BALANCES: Dict[str, float] | None = None

    def __init__(self):
        api_key = os.environ["COINBASE_API_KEY"]
        api_secret = os.environ["COINBASE_API_SECRET"]
        self.auth = _CoinbaseWalletAuth(api_key, api_secret)

    def get_balance(self, symbol) -> float:
        if Coinbase.BALANCES is None:
            Coinbase.BALANCES = {}
            self._fetch_balances()
        return Coinbase.BALANCES.get(symbol, 0.0)

    def _fetch_balances(self, next_uri: str = "") -> None:
        url = self.API_URL + (next_uri or "/v2/accounts")
        log.debug(f"Sending request to {url}")
        resp = requests.get(url, auth=self.auth)
        resp.raise_for_status()
        retval = resp.json()

        for account in retval["data"]:
            if balance := float(account["balance"]["amount"]):
                symbol = account["balance"]["currency"]
                Coinbase.BALANCES[symbol] = balance

        if next_uri := retval["pagination"]["next_uri"]:
            return self._fetch_balances(next_uri)
