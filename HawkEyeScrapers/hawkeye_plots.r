#This script produces plots using the CSV files exported from hawkeye_scraper_helpers.py 
#Pitch map, beehive, 3D ball trajectory, ball speed distribution 
library(tidyr)
library(dplyr)
library(ggplot2)
library(rgl) #for 3D plot

###import files for a single match, examples using match id 10204###
df <- read.csv('10204-traj.csv') #hawkeye_scraper_helpers.py: get_trajectories_df_from_matchid(matchid).to_csv()
stats <- read.csv('10204-stats.csv') #hawkeye_scraper_helpers.py: get_tracking_df_from_matchid(matchid).to_csv()
players <- read.csv('10204-players.csv') #hawkeye_scraper_helpers.py: get_metadata_df_from_matchid(matchid)['player_metadata'].to_csv() 

#combined data file with player information and delivery information from the three CSV files
cdf <- select(players, bowler = id, bowlerName = shortName, rightArmedBowl, bowlingStyle) %>% right_join(df) 
cdf <- select(players, batter = id, batterName = shortName, rightHandedBat) %>% right_join(cdf) 
cdf <- select(players, non.striker = id, nonStrikerName = shortName, nonStrikerRightHandedBat = rightHandedBat) %>% right_join(cdf) 
cdf <- select(stats, match_inn, over_num, over_ball, line_at_stumps, height_at_stumps) %>% right_join(cdf, by = c("match_inn", "over_num", "over_ball"))
#from a CSV containing fixture information, team and other match information can also be added 

#alternatively provided that match_id is present in each row, all CSV files could be read into the same dataframe for comparisons across matches 

###pitch map - from uds/traj data###
selected_data <- drop_na(filter(cdf, bowlerName == "E Perry")) #example filter for information of interest

pitchmap <- ggplot(selected_data, aes(bp.y,-bp.x, color = runs)) + geom_point() + 
  xlim(-1.525,1.525) + ylim(-20.12,0) + #width and length of pitch
  theme(axis.ticks = element_line(color = "green"), 
        axis.ticks.length = unit(.5,"cm"), 
        plot.background = element_rect(fill = "#4CB050"),
        panel.background = element_rect(fill = "#E2D1A7", colour = "blue"), 
        panel.grid.major = element_line(linetype = "dotted"),
        panel.grid.minor = element_line(linetype = "dotted"),
  ) +
  scale_y_continuous(breaks = c(-20, -18, -16, -14, -12, -10, -8, -6, -4, -2, 0)) + #mark out length of the ball in metres
  annotate("rect", xmin=-0.2, xmax=0.2, ymin=-20.12, ymax=0, alpha=0.2, fill="blue") + #mark out line of the wicket
  geom_hline(yintercept = -1.22, color="white", size=1) + geom_hline(yintercept = 0, color="white", size=1) + annotate("segment", x = -1.5, xend = -1.5, y = -1.22, yend = 0, color = "white", size = 1) + annotate("segment", x = 1.5, xend = 1.5, y = -1.22, yend = 0, color = "white", size = 1) + #batting crease
  geom_hline(yintercept = -20.12, color="white", size=1) #bowling crease

###beehive - from uds/stats data###
selected_data <- drop_na(filter(cdf, bowlerName == "E Perry"))  #example filter for information of interest

beehive <- ggplot(selected_data, aes(line_at_stumps,height_at_stumps, color = speed)) + geom_point() +  xlim(-1.525,1.525) + ylim(0, 1.2) + 
  scale_colour_steps(breaks = c(0, 60, 80, 90, 100, 110, 120, 130)) + #for speed data 
  facet_grid(. ~ rightHandedBat) + #filter by left handed and right bat
  annotate("rect", xmin=-0.1143, xmax=0.1143, ymin=0, ymax=0.6935, alpha = 0.05, fill="black") + #light background of wickets area
  annotate("rect", xmin=-0.0175, xmax=0.0175, ymin=0, ymax=0.6935, alpha = 0.3, fill="black") + #off stump
  annotate("rect", xmin=-0.1143, xmax=-0.0793, ymin=0, ymax=0.6935, alpha = 0.3, fill="black") + #middle stump
  annotate("rect", xmin=0.0793, xmax=0.1143, ymin=0, ymax=0.6935, alpha = 0.3, fill="black") + #leg stump
  annotate("rect", xmin=-0.1143, xmax=-0.0048, ymin=0.6935, ymax=0.711, alpha = 0.3, fill="black") + #bails
  annotate("rect", xmin=0.0048, xmax=0.1143, ymin=0.6935, ymax=0.711, alpha = 0.3, fill="black") #bails

###variable bounce###
selected_data <- drop_na(filter(cdf, match_inn == 1) #example filter for information of interest
selected_data$above_stumps <- selected_data$height_at_stumps > 0.745  #did the ball pitch above the stumps?
selected_data$wicket <- selected_data$dismissal_desc != "" #was it a wicket taken? 

#plot whether the ball bounced above or below the stumps
variableBounce <- ggplot(selected_data, aes(bp.y,-bp.x, color = above_stumps)) + geom_point() + 
  facet_grid(. ~ rightHandedBat) + #filter by left handed and right bat
  xlim(-1.525,1.525) + ylim(-20.12,0) + #width and length of pitch
  theme(axis.ticks = element_line(color = "green"), 
        axis.ticks.length = unit(.5,"cm"), 
        plot.background = element_rect(fill = "#4CB050"),
        panel.background = element_rect(fill = "#E2D1A7", colour = "blue"), 
        panel.grid.major = element_line(linetype = "dotted"),
        panel.grid.minor = element_line(linetype = "dotted"),
  ) +
  scale_y_continuous(breaks = c(-20, -18, -16, -14, -12, -10, -8, -6, -4, -2, 0)) + #mark out length of the ball in metres
  annotate("rect", xmin=-0.2, xmax=0.2, ymin=-20.12, ymax=0, alpha=0.2, fill="blue") + #mark out line of the wicket
  geom_hline(yintercept = -1.22, color="white", size=1) + geom_hline(yintercept = 0, color="white", size=1) + annotate("segment", x = -1.5, xend = -1.5, y = -1.22, yend = 0, color = "white", size = 1) + annotate("segment", x = 1.5, xend = 1.5, y = -1.22, yend = 0, color = "white", size = 1) + #batting crease
  geom_hline(yintercept = -20.12, color="white", size=1) #bowling crease

#plot whether wicket was taken
variableBounce + aes(color = wicket)

###3D trajectory - from uds/traj data###
#add to cdf start and end periods for each ball
cdf$start = ( log( ( ( 18.5 - cdf$bp.x ) * ( cdf$a.x / cdf$ebv.x ) ) + 1 ) / cdf$a.x ) + cdf$bt
cdf$end =  ( log( ( ( 0 - cdf$bp.x ) * ( cdf$oba.x / cdf$obv.x ) ) + 1 ) / cdf$oba.x ) + cdf$bt

#function calculates x,y,z coordinates over time; time period is the estimated start and end period of the ball#
#z is the height, x is the length, y is the line of the ball
#function in put is the innings, over number and ball number#
calcPosVect <- function(match_inn, over_num, over_ball) {
  selectedBall <- filter(cdf, match_inn == match_inn, over_num == over_num, over_ball == over_ball)
  posX <- posY <- posZ <- NULL
  for (t in seq(selectedTraj$start[i],selectedTraj$end[i], by = 0.01)) {
    t <- t - selectedTraj$bt[i] #normalise t = 0 to be the time the ball bounces
    if (t <= 0) { #before bounce
      posX <- append(posX, selectedTraj$bp.x[i] - selectedTraj$ebv.x[i] * ( (1 - exp ( selectedTraj$a.x[i] * t ) ) / selectedTraj$a.x[i] ))
      posY <- append(posY, selectedTraj$bp.y[i] + ( selectedTraj$ebv.y[i] * t ) + ( 0.5 * selectedTraj$a.y[i] * t * t ))
      posZ <- append(posZ, selectedTraj$bh[i] + ( selectedTraj$ebv.z[i] * t ) + ( 0.5 * selectedTraj$a.z[i] * t * t ))
    }
    if (t > 0) { #after bounce
      posX <- append(posX, selectedTraj$bp.x[i] - selectedTraj$obv.x[i] * ( (1 - exp ( selectedTraj$oba.x[i] * t ) ) / selectedTraj$oba.x[i] ))
      posY <- append(posY, selectedTraj$bp.y[i] + ( selectedTraj$obv.y[i] * t ) + ( 0.5 * selectedTraj$oba.y[i] * t * t ))
      posZ <- append(posZ, selectedTraj$bh[i] + ( selectedTraj$obv.z[i] * t ) + ( 0.5 * selectedTraj$oba.z[i] * t * t ))
    }}
  
  vect <- tibble(posX,posY,posZ)
  return(vect)
}

selectedBall <- calcPosVect(1,1,1) #example ball selected
plot3d(selectedBall$posX,selectedBall$posY,selectedBall$posZ, xlim = c(0,20), ylim = c(-1.5,1.5))

###ball speed distributions for bowlers###
selected_data <- drop_na(filter(cdf, bowlerName == "E Perry")) #example filter

densityPlot <- ggplot(selected_data, aes(speed)) + geom_density() + xlim(c(30,170)) #set to display 30 km/hr to 170 km/hr, may want to adjust scales