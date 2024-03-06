from setuptools import setup, find_packages

setup(
    name="networth",
    author="ecaz.eth",
    packages=["src"] + find_packages(),
    install_requires=[
        "aiohttp >= 3.8.3",
        "click >= 8.1.3",
        "grazer @ https://github.com/spiceworm/grazer/tarball/master#egg=0.1.1",
        "pycoingecko >= 3.1.0",
        "PyYAML >= 6.0",
        "requests >= 2.28.1",
    ],
    entry_points={"console_scripts": ["networth = src.__main__:main"]},
)
