package main

import (
	"fmt"
	"log"
	"os"
	"time"

	"github.com/bwmarrin/discordgo"
)

func updateStatus(s *discordgo.Session) {
	var apiUrl = os.Getenv("API_URL")
	for {
		var currentStatus = azFunctionApiCall(apiUrl)
		for _, instance := range *currentStatus.Content {
			statusChange := discordgo.UpdateStatusData{
				Activities: []*discordgo.Activity{
					{
						Name: fmt.Sprintf("%s | Active Users: %d/%d", instance.FriendlyName, instance.Metrics.ActiveUsers.RawValue, instance.Metrics.ActiveUsers.MaxValue),
						Type: 0,
					},
				},
			}
			err := s.UpdateStatusComplex(statusChange)
			if err != nil {
				log.Println(err)
			}
			time.Sleep(10 * time.Second)
		}
	}
}
