#This file reads through fixtures JSON files from the ICC website
library(jsonlite)
library(tidyr)
library(dplyr)

#import all files into R, and create a tibble with all the fixtures
temp = list.files(pattern="ICC-fixtures-*") #create list of files in the directory
FIXTURES_ALL <- fromJSON("ICC-fixtures-0")$content #initialise the tibble

for (x in temp) { #exclude ICC-fixtures-0 as already added
  df <- fromJSON(x, flatten = TRUE)
  FIXTURES_ALL <- bind_rows(FIXTURES_ALL, df$content)
}

#filter by gametype, game types include "ODI","T20I","IPLT20","CLT20","FIRST_CLASS",LIST_A","TEST",T20","OTHER","HUNDRED"    
tests <- filter(FIXTURES_ALL, scheduleEntry.matchType == "TEST") %>% 
  summarise(matchID = scheduleEntry.matchId.id,
            matchDate = scheduleEntry.matchDate, 
            label,tournamentLabel,
            venue = scheduleEntry.venue.fullName, country = scheduleEntry.venue.country,
            team1 = scheduleEntry.team1.team.abbreviation, team2 = scheduleEntry.team2.team.abbreviation,
            result = scheduleEntry.matchStatus.text)
