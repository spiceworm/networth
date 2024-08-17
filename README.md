## Networth
Define assets in ~/.networth/assets.yaml using assets-template.yaml as a guide.

### Installation
#### Create file containing API credentials
```bash
cat << EOF >> ~/.networth/credentials
ETHERSCAN_API_KEY=...
FINNHUB_API_KEY=...
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
        -v ~/.networth/assets.yaml:/app/assets.yaml \
        -e ETHERSCAN_API_KEY=$(grep ETHERSCAN_API_KEY ~/.networth/credentials | cut -d= -f2) \
        -e FINNHUB_API_KEY=$(grep FINNHUB_API_KEY ~/.networth/credentials | cut -d= -f2) \
        networth "$@"

popd > /dev/null
EOF
```

#### Set ownership and permissions
```bash
sudo chown $USER:$USER /usr/local/bin/networth
chmod 0755 /usr/local/bin/networth
```
