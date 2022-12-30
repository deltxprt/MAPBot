package main

import (
	"encoding/json"
	"io"
	"log"
	"mapbot/internal/data"
	"net/http"
)

func azFunctionApiCall(apiUrl string) *data.AzApiReponse {
	var Instances data.AzApiReponse
	request, err := http.NewRequest("GET", apiUrl, nil)

	if err != nil {
		log.Fatal(err)
	}

	client := &http.Client{}
	response, error := client.Do(request)

	if error != nil {
		log.Fatal(error)
	}

	defer response.Body.Close()

	body, _ := io.ReadAll(response.Body)

	err = json.Unmarshal([]byte(body), &Instances)
	if err != nil {
		log.Fatal(err)
	}
	return &Instances
}
