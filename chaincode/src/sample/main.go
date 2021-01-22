package main

import (
    "sample/counter"

    "github.com/hyperledger/fabric-contract-api-go/contractapi"
)

func main() {
    ccCounter := new(counter.CcCounter)

    cc, err := contractapi.NewChaincode(ccCounter)

    if err != nil {
        panic(err.Error())
    }

    if err := cc.Start(); err != nil {
        panic(err.Error())
    }
}
