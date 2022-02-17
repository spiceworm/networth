import aiohttp


class CryptoDotOrg:
    API_URL = 'https://crypto.org/explorer'

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def get_cro_balance(self, address):
        url = f'{self.API_URL}/api/v1/accounts/{address}'
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.json()
            balances = data['result']['totalBalance']
            base_cro_balance = sum(float(balance['amount']) for balance in balances)
            return base_cro_balance  * 0.00000001
