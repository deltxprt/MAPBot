package main

import (
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/bwmarrin/discordgo"
)

func getAllServersStatus(s *discordgo.Session, m *discordgo.MessageCreate) {
	var apiUrl = os.Getenv("API_URL")
	allInstancesStatus := azFunctionApiCall(apiUrl)
	for _, instance := range *allInstancesStatus.Content {
		var instanceStatus string
		instanceStatus = fmt.Sprintf("%s:\n```\nGame: %s\nRunning: %t\nCPUUsage: %d%%\nMemoryUsage: %dMB\nActiveUsers: %d/%d\n```", instance.FriendlyName, instance.Module, instance.Running, instance.Metrics.CPUUsage.RawValue, instance.Metrics.MemoryUsage.RawValue, instance.Metrics.ActiveUsers.RawValue, instance.Metrics.ActiveUsers.MaxValue)
		messageResult, err := s.ChannelMessageSend(m.ChannelID, instanceStatus)
		if err != nil {
			log.Fatal(err)
		}
		fmt.Println(messageResult)
	}
}

func getServerStatus(s *discordgo.Session, m *discordgo.MessageCreate) {
	var apiUrl = os.Getenv("API_URL")
	var isFound = false
	allInstancesStatus := azFunctionApiCall(apiUrl)
	for _, instance := range *allInstancesStatus.Content {
		var instanceStatus string
		if strings.Contains(strings.ToUpper(instance.FriendlyName), strings.ToUpper(strings.Split(m.Content, " ")[1])) {
			isFound = true
			instanceStatus = fmt.Sprintf("```\nFriendlyName: %s\nModule: %s\nRunning: %t\nCPUUsage: %d%%\nMemoryUsage: %dMB\nActiveUsers: %d/%d\n```", instance.FriendlyName, instance.Module, instance.Running, instance.Metrics.CPUUsage.RawValue, instance.Metrics.MemoryUsage.RawValue, instance.Metrics.ActiveUsers.RawValue, instance.Metrics.ActiveUsers.MaxValue)
			_, _ = s.ChannelMessageSend(m.ChannelID, instanceStatus)
			fmt.Println("server found")
		}
	}
	if !isFound {
		_, _ = s.ChannelMessageSend(m.ChannelID, "Server not found")
	}
}
