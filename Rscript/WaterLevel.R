setwd(ReferencePath)
waterlevels = read.csv("../Data/Raw_Data/waterlevels.csv")

Threshold = waterlevels %>% 
  slice(1) %>% 
  select(Normal, Alert, Warning)

# generate datetime sequence
start_time = as.POSIXct("02/03/2024 19:00", format = "%d/%m/%Y %H:%M")
timestamps = seq(from = start_time, by = "hour", length.out = nrow(waterlevels))

# create time series data frame
ts_waterlevels = waterlevels %>% 
  mutate(Time = timestamps) %>% 
  select(Time, WL)

# Plot time series data
plot(ts_waterlevels$Time, ts_waterlevels$WL, type = "l", xlab = "Time", 
     ylab = "Water Levels", main = "Hourly Water Levels",ylim=c(100,108))

# Add waterlevel benchmark
with(Treshold, {
  abline(h = c(Normal, Alert, Warning),
         col = c("green", "blue", "red"),
         lty = "dotted",
         lwd = 2)
})