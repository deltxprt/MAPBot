package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/bwmarrin/discordgo"
)

var (
	Token     string
	BotPrefix string

	config *configStruct
)

type configStruct struct {
	Token     string `json : "Token"`
	BotPrefix string `json : "BotPrefix"`
}

type InstancesStatus struct {
	InstanceID   string `json:"InstanceID"`
	FriendlyName string `json:"FriendlyName"`
	Module       string `json:"Module"`
	Running      bool   `json:"Running"`
	Suspended    bool   `json:"Suspended"`
	Metrics      struct {
		CPUUsage struct {
			RawValue int    `json:"RawValue"`
			MaxValue int    `json:"MaxValue"`
			Percent  int    `json:"Percent"`
			Units    string `json:"Units"`
		} `json:"CPU Usage"`
		MemoryUsage struct {
			RawValue int    `json:"RawValue"`
			MaxValue int    `json:"MaxValue"`
			Percent  int    `json:"Percent"`
			Units    string `json:"Units"`
		} `json:"Memory Usage"`
		ActiveUsers struct {
			RawValue int    `json:"RawValue"`
			MaxValue int    `json:"MaxValue"`
			Percent  int    `json:"Percent"`
			Units    string `json:"Units"`
		} `json:"Active Users"`
	} `json:"Metrics"`
}

type AzApiReponse struct {
	Content *[]InstancesStatus
}

func azFunctionApiCall(apiUrl string) *AzApiReponse {
	var Instances AzApiReponse
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

func ReadConfig() error {
	fmt.Println("Reading config file...")
	file, err := os.ReadFile("./config.json")

	if err != nil {
		fmt.Println(err.Error())
		return err
	}

	fmt.Println(string(file))

	err = json.Unmarshal(file, &config)

	if err != nil {
		fmt.Println(err.Error())
		return err
	}
	Token = config.Token
	BotPrefix = config.BotPrefix

	return nil

}

var BotId string
var goBot *discordgo.Session

func Start() {
	goBot, err := discordgo.New("Bot " + config.Token)

	if err != nil {
		fmt.Println(err.Error())
		return
	}

	u, err := goBot.User("@me")

	if err != nil {
		fmt.Println(err.Error())
		return
	}

	BotId = u.ID

	goBot.AddHandler(messageHandler)

	err = goBot.Open()

	if err != nil {
		fmt.Println(err.Error())
		return
	}
	fmt.Println("Bot is running !")
}

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

func main() {
	err := ReadConfig()

	if err != nil {
		fmt.Println(err.Error())
		return
	}

	Start()

	<-make(chan struct{})
	return
}
