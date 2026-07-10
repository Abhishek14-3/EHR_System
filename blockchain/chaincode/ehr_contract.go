package main

import (
	"encoding/json"
	"fmt"
	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type EHRAsset struct {
	ID              string   `json:"id"`
	PatientID       string   `json:"patientId"`
	IPFSHash        string   `json:"ipfsHash"`
	AuthorizedUsers []string `json:"authorizedUsers"`
	MLPrediction    string   `json:"mlPrediction"`
}

type SmartContract struct {
	contractapi.Contract
}

// ✅ CREATE RECORD
func (s *SmartContract) CreateRecord(ctx contractapi.TransactionContextInterface, id string, patientId string, ipfsHash string, prediction string) (string, error) {

	asset := EHRAsset{
		ID:              id,
		PatientID:       patientId,
		IPFSHash:        ipfsHash,
		AuthorizedUsers: []string{patientId},
		MLPrediction:    prediction,
	}

	assetJSON, err := json.Marshal(asset)
	if err != nil {
		return "", err
	}

	err = ctx.GetStub().PutState(id, assetJSON)
	if err != nil {
		return "", err
	}

	return "Record Created Successfully", nil
}

// ✅ GRANT ACCESS
func (s *SmartContract) GrantAccess(ctx contractapi.TransactionContextInterface, id string, doctorId string) (string, error) {

	assetJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return "", err
	}

	if assetJSON == nil {
		return "", fmt.Errorf("record not found")
	}

	var asset EHRAsset
	err = json.Unmarshal(assetJSON, &asset)
	if err != nil {
		return "", err
	}

	for _, user := range asset.AuthorizedUsers {
		if user == doctorId {
			return "Already Authorized", nil
		}
	}

	asset.AuthorizedUsers = append(asset.AuthorizedUsers, doctorId)

	newAssetJSON, err := json.Marshal(asset)
	if err != nil {
		return "", err
	}

	err = ctx.GetStub().PutState(id, newAssetJSON)
	if err != nil {
		return "", err
	}

	return "Access Granted", nil
}

// ✅ GET ALL RECORDS (FIXED)
func (s *SmartContract) GetAllRecords(ctx contractapi.TransactionContextInterface) (string, error) {

	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return "", err
	}
	defer resultsIterator.Close()

	var records []EHRAsset

	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return "", err
		}

		var asset EHRAsset
		err = json.Unmarshal(queryResponse.Value, &asset)
		if err != nil {
			return "", err
		}

		records = append(records, asset)
	}

	finalJSON, err := json.Marshal(records)
	if err != nil {
		return "", err
	}

	return string(finalJSON), nil
}

// ✅ GET RECORDS BY DOCTOR (FIXED)
func (s *SmartContract) GetRecordsByDoctor(ctx contractapi.TransactionContextInterface, doctorId string) (string, error) {

	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return "", err
	}
	defer resultsIterator.Close()

	var records []EHRAsset

	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return "", err
		}

		var asset EHRAsset
		err = json.Unmarshal(queryResponse.Value, &asset)
		if err != nil {
			return "", err
		}

		for _, user := range asset.AuthorizedUsers {
			if user == doctorId {
				records = append(records, asset)
				break
			}
		}
	}

	finalJSON, err := json.Marshal(records)
	if err != nil {
		return "", err
	}

	return string(finalJSON), nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(&SmartContract{})
	if err != nil {
		panic(err.Error())
	}

	if err := chaincode.Start(); err != nil {
		panic(err.Error())
	}
}