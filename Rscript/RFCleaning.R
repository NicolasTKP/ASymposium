library(dplyr)
library(tidyverse)
library(stringr)

klangRF = read.csv("C:\\Users\\USER\\Downloads\\klangRF.csv")
klangRF
klangRF %>%
  filter(station_id == "27233") %>%
  arrange(dt)

summary(klangRF)
is.na(klangRF)

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

klangRF %>%
  filter(station_id == "27233") %>%
  arrange(dt)


summary(klangRF)
View(klangRF)

klang

klangRF_nested <- klangRF %>%
  group_by(station_id) %>%
  nest()

ggplot(klangRF, aes(x = dt, y = clean)) +
  geom_line() +
  geom_hline(aes(yintercept = light), linetype = "dotted", color = "green") +
  geom_hline(aes(yintercept = moderate), linetype = "dotted", color = "blue") +
  geom_hline(aes(yintercept = heavy), linetype = "dotted", color = "orange") +
  geom_hline(aes(yintercept = veryheavy), linetype = "dotted", color = "red") +
  facet_wrap(~ station_id, scales = "free_y") +
  labs(title = "Rain Fall by Station", x = "Time", y = "Rain Fall") +
  theme_minimal()

write.csv(klangRF, "C:\\Users\\USER\\Desktop\\Python\\ASymposium\\cleaned_klangRF.csv", row.names = FALSE)


klangWL = read.csv("C:\\Users\\USER\\Downloads\\klangWL.csv")

klangWL

klangWL = klangWL %>% 
  select(-c(raw1)) %>% 
  mutate(dt = dmy_hm(dt), 
         Date = as.Date(dt), 
         Time = format(dt, "%H:%M")) %>% 
  dplyr::rename(datetime = dt,
                wl = clean1) %>% 
  filter(wl != -9999, 
         str_sub(Time, -2, -1) == "00") %>%
  select(-c(Date, Time))

klangWL = klangWL %>%
  group_by(station_id) %>%
  mutate(normal = ifelse(is.na(normal), first(na.omit(normal)), normal)) %>%
  ungroup()

klangWL %>% distinct(station_id, .keep_all = TRUE)
klangWL



klangWL %>%
  filter(station_id == "27233") %>%
  arrange(desc(datetime))

ggplot(klangWL, aes(x = datetime, y = wl)) +
  geom_line() +
  geom_hline(aes(yintercept = normal), linetype = "dotted", color = "green") +
  geom_hline(aes(yintercept = alert), linetype = "dotted", color = "blue") +
  geom_hline(aes(yintercept = warning), linetype = "dotted", color = "orange") +
  geom_hline(aes(yintercept = danger), linetype = "dotted", color = "red") +
  facet_wrap(~ station_id, scales = "free_y") +
  labs(title = "Water Levels by Station", x = "Time", y = "Water Level") +
  theme_minimal()

