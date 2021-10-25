from datetime import datetime
import hashlib
import hmac
import os
import time

import requests
from requests.auth import AuthBase


class _CoinbaseWalletAuth(AuthBase):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        timestamp = int(time.time())
        message = f'{timestamp}{request.method}{request.path_url}{request.body or ""}'
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
        request.headers.update({
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-VERSION': datetime.today().strftime('%Y-%m-%d'),
        })
        return request


class Coinbase:
    API_URL = 'https://api.coinbase.com'
    BALANCES = None

    def __init__(self):
        api_key = os.environ['COINBASE_API_KEY']
        api_secret = os.environ['COINBASE_API_SECRET']
        self.auth = _CoinbaseWalletAuth(api_key, api_secret)

    def get_balance(self, symbol):
        if Coinbase.BALANCES is None:
            Coinbase.BALANCES = {}
            self._fetch_balances()
        return Coinbase.BALANCES.get(symbol, 0)

    def _fetch_balances(self, next_uri=''):
        resp = requests.get(self.API_URL + (next_uri or '/v2/accounts'), auth=self.auth)
        resp.raise_for_status()
        retval = resp.json()

        for account in retval['data']:
            balance = float(account['balance']['amount'])
            if balance:
                symbol = account['balance']['currency']
                Coinbase.BALANCES[symbol] = balance

        next_uri = retval['pagination']['next_uri']
        if next_uri:
            return self._fetch_balances(next_uri)
