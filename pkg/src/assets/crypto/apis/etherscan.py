import os

import requests
from web3 import Web3


def wei_to_ether(wei):
    return float(Web3.fromWei(int(wei), 'ether'))


class EtherScan:
    API_URL = 'https://api.etherscan.io'
    BALANCES = {}

    def __init__(self):
        self.api_key = os.environ['ETHERSCAN_API_KEY']

    def _build_url(self, **kwargs):
        kwargs.update({'apikey': self.api_key})
        params = '&'.join(f'{k}={v}' for k, v in kwargs.items())
        return f'{self.API_URL}/api?{params}'

    def _send(self, request, **kwargs):
        resp = request(url=self._build_url(**kwargs))
        resp.raise_for_status()
        return resp.json()

    def get_ether_balance(self, address):
        return self.get_ether_balances(address, return_sum=True)

    def get_ether_balances(self, *addresses, return_sum=False):
        params = {'module': 'account', 'action': 'balancemulti', 'address': ','.join(addresses)}
        retval = self._send(requests.get, **params)
        accounts = retval['result']
        if not return_sum:
            for account in accounts:
                account['balance'] = wei_to_ether(account['balance'])
            return accounts
        return wei_to_ether(sum(int(acct['balance']) for acct in accounts))

    def get_token_balance(self, address, contract_address):
        params = {
            'action': 'tokenbalance',
            'address': address,
            'contractaddress': contract_address,
            'module': 'account',
            'tag': 'latest'
        }
        retval = self._send(requests.get, **params)
        return wei_to_ether(retval['result'])
