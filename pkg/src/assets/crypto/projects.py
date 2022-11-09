import logging
from typing import Iterable, Union

import pycoingecko

from .apis import (
    BlockStream,
    Coinbase,
    EtherScan,
    Gemini,
)
from .. import Asset


__all__ = [
    "Aave",
    "AdventureGold",
    "Alchemix",
    "Algorand",
    "AxieInfinity",
    "Bitcoin",
    "Cardano",
    "CRYPTO",
    "Chainlink",
    "Cronos",
    "Decentraland",
    "DYDX",
    "ENS",
    "Ergo",
    "Ethereum",
    "Fantom",
    "GeminiDollar",
    "Illuvium",
    "ImmutableX",
    "LoopRing",
    "Optimism",
    "Polygon",
    "Rari",
    "RocketPool",
    "SmoothLovePotion",
    "Synthetix",
    "TheGraph",
    "TheSandbox",
    "Uniswap",
    "USDC",
]


log = logging.getLogger()


class CryptoAsset(Asset):
    prices = {}

    def __init__(self, balances_or_addresses: Iterable[Union[float, int, str]] = ()):
        balances = [bal for bal in balances_or_addresses if not isinstance(bal, str)]
        self.addresses = [addr for addr in balances_or_addresses if isinstance(addr, str)]

        if self.addresses:
            log.debug(
                "Hardcoded address for %s: %s",
                self.__class__.__name__,
                ", ".join(self.addresses)
            )

        super().__init__(balances)

    async def fetch_prices(self, *ids) -> None:
        if not CryptoAsset.prices:
            api = pycoingecko.CoinGeckoAPI()
            retval = api.get_coins_markets("usd", ids=",".join(ids))
            CryptoAsset.prices = {project["id"]: project["current_price"] for project in retval}

    @property
    async def price(self) -> float:
        return CryptoAsset.prices[self.LABEL]

    @property
    async def quantity(self) -> float:
        coinbase = Coinbase()
        gemini = Gemini(self.SESSION)

        coinbase_bal = coinbase.get_balance(self.SYMBOL) + sum(
            [coinbase.get_balance(sa) for sa in getattr(self, "SYMBOL_ALIASES", ())]
        )
        gemini_bal = await gemini.get_balance(self.SYMBOL) + sum(
            [await gemini.get_balance(sa) for sa in getattr(self, "SYMBOL_ALIASES", ())]
        )

        hardcoded_bal = self._quantity

        return sum(
            [
                coinbase_bal,
                gemini_bal,
                hardcoded_bal,
            ]
        )


class EthereumAsset(CryptoAsset):
    CONTRACT_ADDRESS: str | None = None

    @property
    async def quantity(self) -> float:
        # If assets.yaml defines any `self.addresses` for the current token.
        if self.addresses:
            api = EtherScan(self.SESSION)
            blockchain_bal = sum([await api.get_token_balance(addr, self.CONTRACT_ADDRESS) for addr in self.addresses])
        else:
            blockchain_bal = 0

        return sum(
            [
                await super().quantity,
                blockchain_bal,
            ]
        )


class Aave(EthereumAsset):
    CONTRACT_ADDRESS = "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9"
    LABEL = "aave"
    SYMBOL = "AAVE"


class AdventureGold(EthereumAsset):
    CONTRACT_ADDRESS = "0x32353a6c91143bfd6c7d363b546e62a9a2489a20"
    LABEL = "adventure-gold"
    SYMBOL = "AGLD"


class Alchemix(EthereumAsset):
    CONTRACT_ADDRESS = "0xdbdb4d16eda451d0503b854cf79d55697f90c8df"
    LABEL = "alchemix"
    SYMBOL = "ALCX"


class Algorand(CryptoAsset):
    LABEL = "algorand"
    SYMBOL = "ALGO"


class AxieInfinity(EthereumAsset):
    CONTRACT_ADDRESS = "0xbb0e17ef65f82ab018d8edd776e8dd940327b28b"
    LABEL = "axie-infinity"
    SYMBOL = "AXS"


class Bitcoin(CryptoAsset):
    LABEL = "bitcoin"
    SYMBOL = "BTC"

    @property
    async def quantity(self) -> float:
        blockstream = BlockStream(self.SESSION)
        hardcoded_bal = await super().quantity
        bitcoin_bal = await blockstream.get_balances(*self.addresses, return_sum=True)
        return hardcoded_bal + bitcoin_bal


class Cardano(CryptoAsset):
    LABEL = "cardano"
    SYMBOL = "ADA"


class Chainlink(EthereumAsset):
    CONTRACT_ADDRESS = "0x514910771af9ca656af840dff83e8264ecf986ca"
    LABEL = "chainlink"
    SYMBOL = "LINK"


class Cronos(EthereumAsset):
    CONTRACT_ADDRESS = "0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b"
    LABEL = "crypto-com-chain"
    SYMBOL = "CRO"


class Decentraland(EthereumAsset):
    CONTRACT_ADDRESS = "0x0f5d2fb29fb7d3cfee444a200298f468908cc942"
    LABEL = "decentraland"
    SYMBOL = "MANA"


class DYDX(EthereumAsset):
    CONTRACT_ADDRESS = "0x92d6c1e31e14520e676a687f0a93788b716beff5"
    LABEL = "dydx"
    SYMBOL = "DYDX"


class ENS(EthereumAsset):
    CONTRACT_ADDRESS = "0xc18360217d8f7ab5e7c516566761ea12ce7f9d72"
    LABEL = "ethereum-name-service"
    SYMBOL = "ENS"


class Ergo(CryptoAsset):
    LABEL = "ergo"
    SYMBOL = "ERG"


class Ethereum(CryptoAsset):
    LABEL = "ethereum"
    SYMBOL = "ETH"
    SYMBOL_ALIASES = ("ETH2",)

    @property
    async def quantity(self) -> float:
        etherscan = EtherScan(self.SESSION)
        hardcoded_bal = await super().quantity
        ether_bal = await etherscan.get_ether_balances(*self.addresses, return_sum=True)
        return hardcoded_bal + ether_bal


class Fantom(EthereumAsset):
    CONTRACT_ADDRESS = "0x4e15361fd6b4bb609fa63c81a2be19d873717870"
    LABEL = "fantom"
    SYMBOL = "FTM"


class GeminiDollar(EthereumAsset):
    CONTRACT_ADDRESS = "0x056fd409e1d7a124bd7017459dfea2f387b6d5cd"
    LABEL = "gemini-dollar"
    SYMBOL = "GUSD"


class Illuvium(EthereumAsset):
    CONTRACT_ADDRESS = "0x767fe9edc9e0df98e07454847909b5e959d7ca0e"
    LABEL = "illuvium"
    SYMBOL = "ILV"


class ImmutableX(EthereumAsset):
    CONTRACT_ADDRESS = "0xf57e7e7c23978c3caec3c3548e3d615c346e79ff"
    LABEL = "immutable-x"
    SYMBOL = "IMX"


class LoopRing(EthereumAsset):
    CONTRACT_ADDRESS = "0xbbbbca6a901c926f240b89eacb641d8aec7aeafd"
    LABEL = "loopring"
    SYMBOL = "LRC"


class Optimism(EthereumAsset):
    CONTRACT_ADDRESS = "0x4200000000000000000000000000000000000042"
    LABEL = "optimism"
    SYMBOL = "OP"


class Polygon(EthereumAsset):
    CONTRACT_ADDRESS = "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0"
    LABEL = "matic-network"
    SYMBOL = "MATIC"


class Rari(EthereumAsset):
    CONTRACT_ADDRESS = "0xd291e7a03283640fdc51b121ac401383a46cc623"
    LABEL = "rari-governance-token"
    SYMBOL = "RGT"


class RocketPool(EthereumAsset):
    CONTRACT_ADDRESS = "0xd33526068d116ce69f19a9ee46f0bd304f21a51f"
    LABEL = "rocket-pool"
    SYMBOL = "RPL"


class SmoothLovePotion(EthereumAsset):
    CONTRACT_ADDRESS = "0xcc8fa225d80b9c7d42f96e9570156c65d6caaa25"
    LABEL = "smooth-love-potion"
    SYMBOL = "SLP"


class Synthetix(EthereumAsset):
    CONTRACT_ADDRESS = "0xc011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f"
    LABEL = "havven"
    SYMBOL = "SNX"


class TheGraph(EthereumAsset):
    CONTRACT_ADDRESS = "0xc944e90c64b2c07662a292be6244bdf05cda44a7"
    LABEL = "the-graph"
    SYMBOL = "GRT"


class TheSandbox(EthereumAsset):
    CONTRACT_ADDRESS = "0x3845badade8e6dff049820680d1f14bd3903a5d0"
    LABEL = "the-sandbox"
    SYMBOL = "SAND"


class Uniswap(EthereumAsset):
    CONTRACT_ADDRESS = "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"
    LABEL = "uniswap"
    SYMBOL = "UNI"


class USDC(EthereumAsset):
    CONTRACT_ADDRESS = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
    LABEL = "usd-coin"
    SYMBOL = "USDC"


CRYPTO = [
    Aave,
    AdventureGold,
    Alchemix,
    Algorand,
    AxieInfinity,
    Bitcoin,
    Cardano,
    Chainlink,
    Cronos,
    Decentraland,
    DYDX,
    ENS,
    Ergo,
    Ethereum,
    Fantom,
    GeminiDollar,
    Illuvium,
    ImmutableX,
    LoopRing,
    Optimism,
    Polygon,
    Rari,
    RocketPool,
    SmoothLovePotion,
    Synthetix,
    TheGraph,
    TheSandbox,
    Uniswap,
    USDC,
]
