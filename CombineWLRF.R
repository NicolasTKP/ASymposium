library(dplyr)
library(tidyverse)
library(stringr)
library(mice)

klangRF = read.csv("C:\\Users\\USER\\Desktop\\Python\\ASymposium\\cleaned_klangRF.csv")
klangWL = read.csv("C:\\Users\\USER\\Desktop\\Python\\ASymposium\\cleaned_klangWL.csv")


View(klangRF)

klangRF = klangRF %>%
  rename(
    datetime = dt, 
    rf = clean,
    rfhourly = chourly,
    rfdaily = cdaily,
    rfyearly = cyearly,
    rf15min = c15min
  )

klangWL <- merge(
  klangWL,
  klangRF[, c("station_id", "datetime", "rf", "rf15min", "rfhourly", "rfdaily", "rfyearly", "light", "moderate", "heavy", "veryheavy")],  # only keep needed columns
  by = c("station_id", "datetime"),
  all.x = TRUE  
)
View(klangWL)


selected_cols = klangWL[, c("rf", "rf15min", "rfhourly", "rfdaily", "rfyearly", "light", "moderate", "heavy", "veryheavy")]

imputed = mice(selected_cols, method = "rf", m = 1, maxit = 5, seed = 123)
completed_data = complete(imputed)

completed_data

