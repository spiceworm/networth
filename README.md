## Networth
### Installation
#### Create file containing API credentials
```bash
cat << EOF >> ~/.networth/credentials
COINBASE_API_KEY=...
COINBASE_API_SECRET=...
ETHERSCAN_API_KEY=...
FINNHUB_API_KEY=...
GEMINI_API_KEY=...
GEMINI_API_SECRET=...
EOF
```

#### Create executable file
```bash
cat << EOF >> /usr/local/bin/networth
#!/usr/bin/env bash

set -e

pushd /path/to/networth/ > /dev/null

docker build . -t networth &> /dev/null

docker run --rm -it \
        -v `pwd`/assets.yaml:/app/assets.yaml \
        -e COINBASE_API_KEY=$(grep COINBASE_API_KEY ~/.networth/credentials | cut -d= -f2) \
        -e COINBASE_API_SECRET=$(grep COINBASE_API_SECRET ~/.networth/credentials | cut -d= -f2) \
        -e ETHERSCAN_API_KEY=$(grep ETHERSCAN_API_KEY ~/.networth/credentials | cut -d= -f2) \
        -e FINNHUB_API_KEY=$(grep FINNHUB_API_KEY ~/.networth/credentials | cut -d= -f2) \
        -e GEMINI_API_KEY=$(grep GEMINI_API_KEY ~/.networth/credentials | cut -d= -f2) \
        -e GEMINI_API_SECRET=$(grep GEMINI_API_SECRET ~/.networth/credentials | cut -d= -f2) \
        networth "$@"

popd > /dev/null
EOF
```


#### Set ownership and permissions
```bash
sudo chown $USER:$USER /usr/local/bin/networth
chmod 0755 /usr/local/bin/networth
```
