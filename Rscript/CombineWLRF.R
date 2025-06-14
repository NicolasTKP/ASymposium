library(dplyr)
library(tidyverse)
library(stringr)
library(mice)
library(plyr)

klangRF = read.csv("C:\\Users\\asus\\Desktop\\Python\\ASymposium\\Data\\cleaned_klangRF.csv")
klangWL = read.csv("C:\\Users\\ASUS\\Desktop\\Python\\ASymposium\\Data\\normal_klangWL.csv")
klangWL
klangWL %>% distinct(station_id, .keep_all = TRUE)
klangWL %>%
  filter(station_id == "SELATMUARA") %>%
  arrange(desc(datetime))

View(klangRF)

klangRF = klangRF %>%
    dplyr::rename(
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


selected_cols = klangWL %>% select(rf, rf15min, rfhourly, rfdaily, rfyearly, light, moderate, heavy, veryheavy)
str(selected_cols)
colSums(is.na(selected_cols))

selected_cols = selected_cols %>%
  mutate(
    light = as.factor(light),
    moderate = as.factor(moderate),
    heavy = as.factor(heavy),
    veryheavy = as.factor(veryheavy)
  )

method = make.method(selected_cols)

method[c("rf", "rf15min", "rfhourly", "rfdaily", "rfyearly")] <- "pmm"

imputed = mice(selected_cols, method = method, m = 5, maxit = 10)
completed_data = complete(imputed, 1)

completed_data
colSums(is.na(completed_data))

klangWL$rf = completed_data$rf
klangWL$rf15min = completed_data$rf15min
klangWL$rfdaily = completed_data$rfdaily
klangWL$rfyearly = completed_data$rfyearly

klangWL = klangWL %>%
  mutate(rfhourly = ifelse(is.na(rfhourly), rf15min, rfhourly))

get_mode = function(x) {
  uniq = unique(na.omit(x)) 
  uniq[which.max(tabulate(match(x, uniq)))]
}

klangWL$light[is.na(klangWL$light)] = get_mode(klangWL$light)
klangWL$moderate[is.na(klangWL$moderate)] = get_mode(klangWL$moderate)
klangWL$heavy[is.na(klangWL$heavy)] = get_mode(klangWL$heavy)
klangWL$veryheavy[is.na(klangWL$veryheavy)] = get_mode(klangWL$veryheavy)

colSums(is.na(klangWL))
summary(klangWL)
write.csv(klangWL, "C:\\Users\\asus\\Desktop\\Python\\ASymposium\\Data\\normal_klangWLRF.csv", row.names = FALSE)
