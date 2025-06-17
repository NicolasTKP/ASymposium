klangRF = read.csv("../Data/Raw_Data/klangRF.csv")
klangWL = read.csv("../Data/Raw_Data/klangWL.csv")

########################### Data Cleaning ###########################

### Klang rain fall data ###
klangRF = klangRF %>% 
  select(-c(raw)) %>% 
  mutate(dt = dmy_hm(dt), 
       Date = as.Date(dt), 
       Time = format(dt, "%H:%M")) %>% 
  filter(clean != -9999, 
         str_sub(Time, -2, -1) == "00",
         clean >= 0,
         chourly >= 0,
         cyearly != -9999,
         c15min != -9999) %>% 
  select(-c(Date, Time))

### Klang water level data ###

# for graph plotting
klangWL2 = klangWL %>% 
  select(-c(raw1)) %>% 
  mutate(dt = dmy_hm(dt), 
         Date = as.Date(dt), 
         Time = format(dt, "%H:%M")) %>% 
  dplyr::rename(datetime = dt,
         wl = clean1) %>% 
  filter(wl != -9999, 
         str_sub(Time, -2, -1) == "00",
         ! is.na(normal), 
         datetime < as.Date("2024-05-01")) %>%
  select(-c(Date, Time)) %>%
  mutate(normal = ifelse(is.na(normal), first(na.omit(normal)), normal))

# for data used later
klangWL = klangWL %>% 
  select(-c(raw1)) %>% 
  mutate(dt = dmy_hm(dt), 
         Date = as.Date(dt), 
         Time = format(dt, "%H:%M")) %>% 
  dplyr::rename(datetime = dt,
                wl = clean1) %>% 
  filter(wl != -9999, 
         str_sub(Time, -2, -1) == "00",
         station_id %in% c("PEKANMERU")) %>%
  select(-c(Date, Time)) %>%
  mutate(normal = ifelse(is.na(normal), first(na.omit(normal)), normal))

########################### Data Visualization ###########################

ggplot(klangRF, aes(x = dt, y = clean)) +
  geom_line() +
  geom_hline(aes(yintercept = light), linetype = "dotted", color = "green") +
  geom_hline(aes(yintercept = moderate), linetype = "dotted", color = "blue") +
  geom_hline(aes(yintercept = heavy), linetype = "dotted", color = "orange") +
  geom_hline(aes(yintercept = veryheavy), linetype = "dotted", color = "red") +
  facet_wrap(~ station_id, scales = "free_y") +
  labs(title = "Rain Fall by Station", x = "Time", y = "Rain Fall") +
  theme_minimal()

ggplot(klangWL2, aes(x = datetime, y = wl)) +
  geom_line() +
  geom_hline(aes(yintercept = normal), linetype = "dotted", color = "green") +
  geom_hline(aes(yintercept = alert), linetype = "dotted", color = "blue") +
  geom_hline(aes(yintercept = warning), linetype = "dotted", color = "orange") +
  geom_hline(aes(yintercept = danger), linetype = "dotted", color = "red") +
  facet_wrap(~ station_id, scales = "free_y") +
  labs(title = "Water Levels by Station", x = "Time", y = "Water Level") +
  theme_minimal()

########################### Export Data ###########################
setwd(OutputFile)
write.csv(klangRF,"../Data/R_output/cleaned_klangRF.csv", row.names = FALSE)
write.csv(klangWL, "../Data/R_output/cleaned_klangWL.csv", row.names = FALSE)
  
setwd(WorkingPath)