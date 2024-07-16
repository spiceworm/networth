from setuptools import setup, find_packages

setup(
    name="networth",
    author="ecaz.eth",
    packages=["src"] + find_packages(),
    install_requires=[
        "aiohttp >= 3.9.5",
        "click >= 8.1.7",
        "finnhub-python >= 2.4.20",
        "pycoingecko >= 3.1.0",
        "PyYAML >= 6.0.1",
        "requests >= 2.32.3",
    ],
    entry_points={"console_scripts": ["networth = src.__main__:main"]},
)
