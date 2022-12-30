package main

import (
	"fmt"
	"strings"

	"github.com/bwmarrin/discordgo"
)

func messageHandler(s *discordgo.Session, m *discordgo.MessageCreate) {
	if m.Author.ID == BotId {
		return
	}
	switch strings.Split(m.Content, " ")[0] {
	case BotPrefix + "ping":
		{
			_, _ = s.ChannelMessageSend(m.ChannelID, "pong")
		}
	case BotPrefix + "yo":
		{
			_, _ = s.ChannelMessageSend(m.ChannelID, "What's up ma dude!")
			fmt.Println("Yo command executed !")
		}
	case BotPrefix + "getallstatus":
		{
			getAllServersStatus(s, m)
		}
	case BotPrefix + "test":
		{
			testArray := []string{"test1", "test2", "test3"}
			for _, test := range testArray {
				_, _ = s.ChannelMessageSend(m.ChannelID, test)
			}
		}
	case BotPrefix + "getstatus":
		{
			getServerStatus(s, m)
		}
	default:
		{
			_, _ = s.ChannelMessageSend(m.ChannelID, "Command not found !")
			fmt.Println(m.Content)
		}
	}
}
