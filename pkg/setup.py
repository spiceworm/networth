from setuptools import setup, find_packages

setup(
    name='networth',
    author='ecaz.eth',
    packages=['src'] + find_packages(),
    install_requires=[
        'click >= 8.0.1',
        'pycoingecko >= 2.2.0',
        'PyYAML >= 5.4.1',
        'requests >= 2.24.0',
        'web3 >= 5.23.0',
        'IPython',
    ],
    entry_points={
        'console_scripts': [
            'networth = src.__main__:main'
        ]
    }
)
