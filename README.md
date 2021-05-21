# Requirements

## python (miniconda)

https://docs.conda.io/en/latest/miniconda.html#linux-installers

## docker & docker-compose

https://docs.docker.com/engine/install/ubuntu/
https://docs.docker.com/compose/install/

## Go

Go 1.15
https://golang.org/doc/go1.15

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

# Start up your channel

## Enter the cli container

All processing (e.g. creating a channel, joining a channel, creating a chaincode and so on) is executed inside the cli container.
You can enter the cli container with the following command.

```
docker exec -it cli bash
```

## Create a channel

The channel is created by the following command.

```
python3 scripts/peer-ctrl.py channel create <channel name>
```

## Join the channel

The peers join the created channel by the following command.
All peers joining the channel need to run this command.

```
python3 scripts/peer-ctrl.py channel join <channel name>
```

# Build your chaincode

## Prepare a package of a chaincode to be committed

You can create the package of the chaincode with any name you like.
This command supports golang only.
We provide a sample chaincode in the src/sample directory.
The package is created in the cache directory with the name <chaincode name>.tar.gz.

```
python3 scripts/peer-ctrl.py cc packing <chaincode name> <chaincode path>
```

The following command install the package.

```
python3 scripts/peer-ctrl.py cc install cache/<chaincode name>.tar.gz
```

When the install command is invoked, the package identifier is generated.
In the following example, `sample:08ad586a9e1558ef6754bcf6842581899369516b43e6d9f405a8b7f7edb8daae` is the package identifier.
This package identifier will be used later.

```
2021-03-24 10:32:56.981 UTC [cli.lifecycle.chaincode] submitInstallProposal -> INFO 001 Installed remotely: response:<status:200 payload:"\nGsample:08ad586a9e1558ef6754bcf6842581899369516b43e6d9f405a8b7f7edb8daae\022\006sample" >
2021-03-24 10:32:56.981 UTC [cli.lifecycle.chaincode] submitInstallProposal -> INFO 002 Chaincode code package identifier: sample:08ad586a9e1558ef6754bcf6842581899369516b43e6d9f405a8b7f7edb8daae
```

You can check all installed package in your organization by the following command.

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

Now you can approve the package to be comitted.
The chaincode has a version number and a sequence number.

```
python3 scripts/peer-ctrl.py cc approve <channel> <chaincode name> <version number> <sequence number> <package identifier>
```

All three commands above need to be invoked on all necessary organizations.
You can check which organization has approved the chaincode with the following command.

```
python3 scripts/peer-ctrl.py check commit-readiness <channel> <chaincode name> <version name> <sequence number>
```

## Commit the chaincode

When all necessary organizations approve commit of the chaincode, you can commit the chaincode.

```
python3 scripts/peer-ctrl.py cc commit <channel> <chaincode name> <version number> <sequence number>
```

You can check committed packages of all chaincodes by the following comamand.

```
python3 scripts/peer-ctrl.py check committed-package <channel>
```

The output example is below.
In this example, the chaincode named `sample` is comitted.
This chaincode has version 1.0 and sequence 1.
Moreover, you can see that `init_required` is true.

```
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

If `init_required` is true, you must invoke `init-ledger`.

```
python3 scripts/peer-ctrl.py cc init-ledger <chaincode name>
```

Now you are ready to execute the chaincode.

# Execute the chaincode

There are two ways to execute chaincode: query and invoke.
To read from the ledger, you can use `query`.
To write to the ledger, you can use `invoke`.

The chaincode used in this example counts up a value of the specified key.
Before counting up the value, the key must be reset.

The following example prepare the key X and counts up the value of the key X three times.
In the end, the value of the key X is reset to zero.

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

python3 scripts/peer-ctrl.py cc query sample Get X
---------------------------------------------------
 query: Get
---------------------------------------------------
3

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
