package main

import (
	"encoding/json"
	"io"
	"log"
	"mapbot/internal/data"
	"net/http"

	"github.com/bwmarrin/discordgo"
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

func serverAdministration(s *discordgo.Session, m *discordgo.MessageCreate, action, serverName string) {
	switch action {
	case "start":

	case "stop":

	case "restart":

	case "status":
	}
}
