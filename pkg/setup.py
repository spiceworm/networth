from setuptools import setup, find_packages

setup(
    name="networth",
    author="spiceworm",
    packages=["src"] + find_packages(),
    install_requires=[
        "aioetherscan >= 0.9.4",
        "aiohttp >= 3.10.3",
        "click >= 8.1.7",
        "finnhub-python >= 2.4.20",
        "pycoingecko >= 3.1.0",
        "PyYAML >= 6.0.2",
    ],
    entry_points={"console_scripts": ["networth = src.__main__:main"]},
)
