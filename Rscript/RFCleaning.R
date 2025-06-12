library(dplyr)
library(tidyverse)
library(stringr)

klangRF = read.csv("C:\\Users\\USER\\Desktop\\Python\\ASymposium\\kedahRF.csv")
klangRF

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

write.csv(klangRF, "C:\\Users\\USER\\Desktop\\Python\\ASymposium\\cleaned_kedahRF.csv", row.names = FALSE)
