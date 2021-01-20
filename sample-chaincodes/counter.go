package main

import (
    "strconv"

       "github.com/hyperledger/fabric-chaincode-go/shim"
    pb "github.com/hyperledger/fabric-protos-go/peer"
)

type CounterCc struct {
}

func (c *CounterCc) Init(stub shim.ChaincodeStubInterface) pb.Response {
    return shim.Success([]byte("Init successfully."))
}

func (c *CounterCc) Invoke(stub shim.ChaincodeStubInterface) pb.Response {

    function, args := stub.GetFunctionAndParameters()

    if function == "get" {
        return stub.GetState(args[0])
    } else if function == "reset" {
        stub.PutState(args[0], "0")
        return shim.Success(nil)
    } else if function == "countup" {
        value = stub.GetState(args[0])
        value = strconv.Atoi(value)
        value = value + 1
        stub.PutState(args[0], strconv.Itoa(value))
        return value
    }

    return shim.Error("Invalid function: " + function)
}

