# Requirements

## python (miniconda)

https://docs.conda.io/en/latest/miniconda.html#linux-installers

## docker & docker-compose

https://docs.docker.com/engine/install/ubuntu/
https://docs.docker.com/compose/install/

# Getting Start

The following steps guide you through the installation and the building network.

## Setup your development environment

The following command installs the Hyperledger Fabric binaries and the Hyperledger Fabric docker images by following the command.

```
python ctrl.py install
```

## Deploy key materials

You can get key materials from the orderer.
The key materials are packed into tar.gz files, which are sent into `/tmp` directoy.
The following command extracts the tar.gz files and deploy the key materials to specified path.

```
python ctrl.py deploy
```

## Start a peer container and a cli container

You can run a peer container and a cli container by the up option.
The peer container is a member of the network.
The cli container is an command line interface for the network.

```
python ctrl.py up
```

## Enter the cli container

All processing (e.g. creating a channel, joining a channel, creating a chaincode and so on) is done inside the cli container.
You can enter the cli container with the following command.

```
docker exec -it cli bash
```

# Build your a channel

## Create a channel

```
python3 scripts/peer-ctrl.py channel create xkeycloak
```

## Join the channel

```
python3 scripts/peer-ctrl.py channel join xkeycloak
```

```
python3 scripts/peer-ctrl.py cc packing sample src/sample
```

```
python3 scripts/peer-ctrl.py cc install cache/sample.tar.gz
```

```
2021-03-24 10:32:56.981 UTC [cli.lifecycle.chaincode] submitInstallProposal -> INFO 001 Installed remotely: response:<status:200 payload:"\nGsample:08ad586a9e1558ef6754bcf6842581899369516b43e6d9f405a8b7f7edb8daae\022\006sample" >
2021-03-24 10:32:56.981 UTC [cli.lifecycle.chaincode] submitInstallProposal -> INFO 002 Chaincode code package identifier: sample:08ad586a9e1558ef6754bcf6842581899369516b43e6d9f405a8b7f7edb8daae
```

```
python3 scripts/peer-ctrl.py cc approve sample 1.0 1 sample:08ad586a9e1558ef6754bcf6842581899369516b43e6d9f405a8b7f7edb8daae
```

```
python3 scripts/peer-ctrl.py cc commit sample 1.0 1
```

```
------------------------------------
 querycommitted
------------------------------------
{
        "chaincode_definitions": [
                {
                        "name": "sample",
                        "sequence": 1,
                        "version": "1.0",
                        "endorsement_plugin": "escc",
                        "validation_plugin": "vscc",
                        "validation_parameter": "EiAvQ2hhbm5lbC9BcHBsaWNhdGlvbi9FbmRvcnNlbWVudA==",
                        "collections": {},
                        "init_required": true
                }
        ]
}
```

```
python3 scripts/peer-ctrl.py cc init-ledger sample
```

```
bash-5.0# python3 scripts/peer-ctrl.py cc invoke sample Reset X
---------------------------------------------------
 invoke: Reset
---------------------------------------------------
2021-03-24 11:28:05.538 UTC [chaincodeCmd] chaincodeInvokeOrQuery -> INFO 001 Chaincode invoke successful. result: status:200
bash-5.0# python3 scripts/peer-ctrl.py cc invoke sample Countup X
---------------------------------------------------
 invoke: Countup
---------------------------------------------------
2021-03-24 11:28:29.215 UTC [chaincodeCmd] chaincodeInvokeOrQuery -> INFO 001 Chaincode invoke successful. result: status:200 payload:"1"
bash-5.0# python3 scripts/peer-ctrl.py cc invoke sample Countup X
---------------------------------------------------
 invoke: Countup
---------------------------------------------------
2021-03-24 11:28:31.535 UTC [chaincodeCmd] chaincodeInvokeOrQuery -> INFO 001 Chaincode invoke successful. result: status:200 payload:"2"
bash-5.0# python3 scripts/peer-ctrl.py cc invoke sample Countup X
---------------------------------------------------
 invoke: Countup
---------------------------------------------------
2021-03-24 11:28:34.717 UTC [chaincodeCmd] chaincodeInvokeOrQuery -> INFO 001 Chaincode invoke successful. result: status:200 payload:"3"
```

```
python3 scripts/peer-ctrl.py cc query sample Get X
---------------------------------------------------
 query: Get
---------------------------------------------------
3
```

```
python3 scripts/peer-ctrl.py cc invoke sample Reset X
---------------------------------------------------
 invoke: Reset
---------------------------------------------------
2021-03-24 11:30:00.338 UTC [chaincodeCmd] chaincodeInvokeOrQuery -> INFO 001 Chaincode invoke successful. result: status:200
bash-5.0# python3 scripts/peer-ctrl.py cc query sample Get X
---------------------------------------------------
 query: Get
---------------------------------------------------
0
```

# Check

```
python3 scripts/peer-ctrl.py check commit-readiness sample 1.0 1
```

```
python3 scripts/peer-ctrl.py check installed-package
------------------------------------
 queryinstalled
------------------------------------
{
    "installed_chaincodes": [
        {
            "package_id": "sample:08ad586a9e1558ef6754bcf6842581899369516b43e6d9f405a8b7f7edb8daae",
            "label": "sample",
            "references": {
                "xkeycloak": {
                    "chaincodes": [
                        {
                            "name": "sample",
                            "version": "1.0"
                        }
                    ]
                }
            }
        }
    ]
}
```

```
python3 scripts/peer-ctrl.py check committed-package
------------------------------------
 querycommitted
------------------------------------
{
    "chaincode_definitions": [
        {
            "name": "sample",
            "sequence": 1,
            "version": "1.0",
            "endorsement_plugin": "escc",
            "validation_plugin": "vscc",
            "validation_parameter": "EiAvQ2hhbm5lbC9BcHBsaWNhdGlvbi9FbmRvcnNlbWVudA==",
            "collections": {},
            "init_required": true
        }
    ]
}
```
