package main

import (
	"fmt"
	"os"
	"strings"

	"github.com/bwmarrin/discordgo"
)

func getAllServersStatus(s *discordgo.Session, m *discordgo.MessageCreate) {
	var apiUrl = os.Getenv("API_URL")
	allInstancesStatus := azFunctionApiCall(apiUrl)
	var finalEmbedMessage []*discordgo.MessageEmbed
	for _, instance := range *allInstancesStatus.Content {
		var EmbedMessage = discordgo.MessageEmbed{
			Title: "Server Status of " + instance.FriendlyName,
			Fields: []*discordgo.MessageEmbedField{
				{Name: "Game", Value: instance.Module, Inline: false},
				{Name: "Running", Value: fmt.Sprintf("%t", instance.Running), Inline: false},
				{Name: "CPUUsage", Value: fmt.Sprintf("%d%%", instance.Metrics.CPUUsage.RawValue), Inline: false},
				{Name: "MemoryUsage", Value: fmt.Sprintf("%dMB", instance.Metrics.MemoryUsage.RawValue), Inline: false},
				{Name: "ActiveUsers", Value: fmt.Sprintf("%d/%d", instance.Metrics.ActiveUsers.RawValue, instance.Metrics.ActiveUsers.MaxValue), Inline: false},
			},
			Color: 0x992D22,
		}
		finalEmbedMessage = append(finalEmbedMessage, &EmbedMessage)
	}
	_, _ = s.ChannelMessageSendEmbeds(m.ChannelID, finalEmbedMessage)
}

func getServerStatus(s *discordgo.Session, m *discordgo.MessageCreate) {
	var apiUrl = os.Getenv("API_URL")
	var isFound = false
	allInstancesStatus := azFunctionApiCall(apiUrl)
	var finalEmbedMessage []*discordgo.MessageEmbed
	for _, instance := range *allInstancesStatus.Content {
		if strings.Contains(strings.ToUpper(instance.FriendlyName), strings.ToUpper(strings.Split(m.Content, " ")[1])) {
			isFound = true
			var EmbedMessage = discordgo.MessageEmbed{
				Title: "Server Status of " + instance.FriendlyName,
				Fields: []*discordgo.MessageEmbedField{
					{Name: "Game", Value: instance.Module, Inline: false},
					{Name: "Running", Value: fmt.Sprintf("%t", instance.Running), Inline: false},
					{Name: "CPUUsage", Value: fmt.Sprintf("%d%%", instance.Metrics.CPUUsage.RawValue), Inline: false},
					{Name: "MemoryUsage", Value: fmt.Sprintf("%dMB", instance.Metrics.MemoryUsage.RawValue), Inline: false},
					{Name: "ActiveUsers", Value: fmt.Sprintf("%d/%d", instance.Metrics.ActiveUsers.RawValue, instance.Metrics.ActiveUsers.MaxValue), Inline: false},
				},
				Color: 0x992D22,
			}
			finalEmbedMessage = append(finalEmbedMessage, &EmbedMessage)

			// instanceStatus = fmt.Sprintf("%s:\n```\nGame: %s\nRunning: %t\nCPUUsage: %d%%\nMemoryUsage: %dMB\nActiveUsers: %d/%d\n```", instance.FriendlyName, instance.Module, instance.Running, instance.Metrics.CPUUsage.RawValue, instance.Metrics.MemoryUsage.RawValue, instance.Metrics.ActiveUsers.RawValue, instance.Metrics.ActiveUsers.MaxValue)
		}
	}
	_, _ = s.ChannelMessageSendEmbeds(m.ChannelID, finalEmbedMessage)
	if !isFound {
		_, _ = s.ChannelMessageSend(m.ChannelID, "Server not found")
	}
}
