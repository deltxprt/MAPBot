package main

import (
	"fmt"
	"log"
	"strings"

	"github.com/bwmarrin/discordgo"
)

func messageHandler(s *discordgo.Session, m *discordgo.MessageCreate) {
	if m.Author.ID == s.State.User.ID {
		return
	}
	switch strings.Split(m.Content, " ")[0] {
	case *BotPrefix + "ping":
		{
			_, _ = s.ChannelMessageSend(m.ChannelID, "pong")
		}
	case *BotPrefix + "yo":
		{
			_, _ = s.ChannelMessageSend(m.ChannelID, "What's up ma dude!")
			fmt.Println("Yo command executed !")
		}
	case *BotPrefix + "getallstatus":
		{
			getAllServersStatus(s, m)
		}
	case *BotPrefix + "test":
		{
			testArray := []string{"test1", "test2", "test3"}
			for _, test := range testArray {
				_, _ = s.ChannelMessageSend(m.ChannelID, test)
			}
		}
	case *BotPrefix + "getstatus":
		{
			getServerStatus(s, m)
		}
	case "/test":
		{
			registeredCommands := make([]*discordgo.ApplicationCommand, len(commands))
			for i, v := range commands {
				cmd, err := s.ApplicationCommandCreate(s.State.User.ID, *GuildID, v)
				if err != nil {
					log.Panicf("Cannot create '%v' command: %v", v.Name, err)
				}
				registeredCommands[i] = cmd
			}
			if *RemoveCommands {
				log.Println("Removing commands...")
				// // We need to fetch the commands, since deleting requires the command ID.
				// // We are doing this from the returned commands on line 375, because using
				// // this will delete all the commands, which might not be desirable, so we
				// // are deleting only the commands that we added.
				// registeredCommands, err := s.ApplicationCommands(s.State.User.ID, *GuildID)
				// if err != nil {
				// 	log.Fatalf("Could not fetch registered commands: %v", err)
				// }

				for _, v := range registeredCommands {
					err := s.ApplicationCommandDelete(s.State.User.ID, *GuildID, v.ID)
					if err != nil {
						log.Panicf("Cannot delete '%v' command: %v", v.Name, err)
					}
				}
			}
		}
		// default:
		// 	{
		// 		_, _ = s.ChannelMessageSend(m.ChannelID, "Command not found !")
		// 		fmt.Println(m.Content)
		// 	}
	}
}
