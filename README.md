# Requirements

## python (miniconda)

https://docs.conda.io/en/latest/miniconda.html#linux-installers

## docker & docker-compose

https://docs.docker.com/engine/install/ubuntu/
https://docs.docker.com/compose/install/

# Getting Start

The following steps guide you through the installation and the building network.

## Setup your Development Environment

The following command installs the Hyperledger Fabric binaries and the Hyperledger Fabric docker images by following the command.

```
python network.py install
```

## Deploy key material

You can get key material from orderer.
The key material is packed into tar.gz files, which are sent to `/tmp` directoy.
The following command extracts the tar.gz files and deploy the keymaterial to specified path.

```
python network.py deploy
```

## Run peer

You can run a peer by the up option.
The peer works with Docker.

```
python network.py up
```

