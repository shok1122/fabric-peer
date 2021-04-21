package counter

import (
    "testing"

    "github.com/hyperledger/fabric-contract-api-go/contractapi"

    "github.com/hyperledger/fabric-chaincode-go/shimtest"
    "github.com/hyperledger/fabric-chaincode-go/shimtest/mock"

    "github.com/stretchr/testify/assert"
)

type MockTransactionContext struct {
    contractapi.TransactionContext
}

type TestMaterials struct {
    mockStub *shimtest.MockStub
    ctx *MockTransactionContext
    cc *CcCounter
}

func NewTestMaterials() *TestMaterials {

    mockStub := shimtest.NewMockStub("mockstub", new(mock.Chaincode))
    cc := new(CcCounter)
    ctx := new(MockTransactionContext)
    ctx.SetStub(mockStub)

    m := new(TestMaterials)
    m.mockStub = mockStub
    m.cc = cc
    m.ctx = ctx

    return m
}

func TryReset(m *TestMaterials, key string) error {
    m.mockStub.MockTransactionStart("txID_Reset")
    err := m.cc.Reset(m.ctx, key)
    m.mockStub.MockTransactionEnd("txID_Reset")
    return err
}

func TryCountup(m *TestMaterials, key string) (string, error) {
    m.mockStub.MockTransactionStart("txID_Countup")
    count, err := m.cc.TryCountup(m.ctx, key)
    m.mockStub.MockTransactionEnd("txID_Countup")
    return count, err
}

func TryGet(m *TestMaterials, key string) (string, error) {
    m.mockStub.MockTransactionStart("txID_Get")
    count, err := m.cc.Get(m.ctx, key)
    m.mockStub.MockTransactionEnd("txID_Get")
    return count, err
}

func TestReset(t *testing.T) {

    var err error

    m := NewTestMaterials()

    err = TryReset(m, "X")
    assert.Nil(t, err, "failed")
}

func TestGet(t *testing.T) {

    var err error
    var count string

    m := NewTestMaterials()

    err = TryReset(m, "X")
    assert.Nil(t, err, "failed")

    count, err = TryGet(m, "X")
    assert.Nil(t, err, "failed")
    assert.Equal(t, "0", count, "failed")
}

func TestCountup(t *testing.T) {

    var err error
    var count string

    m := NewTestMaterials()

    err = TryReset(m, "X")
    assert.Nil(t, err, "failed")

    count, err = TryCountup(m, "X")
    assert.Nil(t, err, "failed")
    assert.Equal(t, "1", count, "failed")
}

