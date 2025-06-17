klangWL = read.csv("../Data/Raw_Data/klangWL.csv")

###############################################################################
####################             Data Cleaning             ####################
###############################################################################
str(KlangWL)
# Clean Klang Water Level
KlangWL = klangWL %>% 
  select(-c(raw1)) %>% 
  mutate(dt = dmy_hm(dt), 
         Date = as.Date(dt), 
         Time = format(dt, "%H:%M")) %>% 
  rename(Station_ID = station_id, 
         Station_Name = station_name, 
         DateTime = dt, 
         WL = clean1, 
         Normal = normal, 
         Alert = alert, 
         Warning = warning, 
         Danger = danger) %>% 
  filter(WL != -9999, 
         !is.na(Normal), 
         str_sub(Time, -2, -1) == "00", 
         Date < as.Date("2024-05-01"))

check = KlangWL %>% 
  filter(WL >50 | WL < -50)

Stat_Name = KlangWL %>% 
  select(Station_ID, Station_Name) %>% 
  distinct() %>% 



###############################################################################
####################             Visualization             ####################
###############################################################################

# Nest by station
KlangWL_nested <- KlangWL %>%
  group_by(Station_ID) %>%
  nest()

ggplot(KlangWL, aes(x = DateTime, y = WL)) +
  geom_line() +
  geom_hline(aes(yintercept = Normal), linetype = "dotted", color = "green") +
  geom_hline(aes(yintercept = Alert), linetype = "dotted", color = "blue") +
  geom_hline(aes(yintercept = Warning), linetype = "dotted", color = "orange") +
  geom_hline(aes(yintercept = Danger), linetype = "dotted", color = "red") +
  facet_wrap(~ Station_ID, scales = "free_y") +
  labs(title = "Water Levels by Station", x = "Time", y = "Water Level") +
  theme_minimal()

###############################################################################
######################             Checking             #######################
###############################################################################

############### Control ###############
KlangWL_nested$Station_ID
check_station = "3013003_"

############## Checking ##############
data_check = str_c("X", check_station)
ts_check = str_c("ts_X", check_station)

data_check = KlangWL_nested %>% 
  filter(Station_ID == check_station) %>%
  pull(data) %>% 
  .[[1]] %>% 
  group_by(across(-c(DateTime, Time, WL))) %>% 
  summarise(mean_WL = round((mean(WL, na.rm = TRUE)), 2)) %>% 
  ungroup() %>% 
  select(c(Date, mean_WL)) 

ts_check <- ts(data_check$mean_WL, start = c(2024, yday(min(data_check$Date))), frequency = 365) 
plot(ts_check)
