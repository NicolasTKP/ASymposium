################################## Import Data #################################
exposure_path <- "../Data/Raw_Data/Exposure.xlsx"  

# Stock of 2025 new launched residence property
residence_stock = read_excel(exposure_path, sheet = "Selangor_Residential_Property", 
                             range = "A1:M11")

# Total unit of Living Quarter in Malaysia by state
living_quarters = read_excel(exposure_path, sheet = "Living_Quarters_Unit", 
                             range = "A1:C188")

# Terraced House Price in Malaysia by state
terraced_price = read_excel(exposure_path, sheet = "Selangor_Terraced_House_Price")

# Total unit of Kedah agriculture
kedah_agriculture = read_excel(exposure_path, sheet = "Kedah_Agriculture")


klang_WL_probability = read_csv("probability_klangWL.csv")


# Define all the states in Malaysia
state_list = c("Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", 
               "Pahang", "Penang", "Perak", "Perlis", "Sabah", "Sarawak",
               "Selangor", "Terengganu", "Kuala Lumpur", "Labuan", "Putrajaya")

############################## Data Transformation #############################

####################################
############## Part 1 ##############
#################################### 

# Calculate estimation proportion of each state residence property among whole Selangor
district_proportion = residence_stock %>% 
  mutate(Proportion = round((Total / Total[which(District == "Total")]),4)) %>% 
  select(District, Proportion)

# Calculate Selangor district no. of living quarters year by year
district_living_quarters = living_quarters %>% 
  dplyr::rename(State_living_quarter = `Number_of_living_quarters`) %>% 
  filter(State == "Selangor") %>%  
  right_join(expand.grid(Year = unique(living_quarters$Year),
                         District = unique(district_proportion$District)), 
             by = "Year") %>% 
  left_join(district_proportion, by = ("District")) %>% 
  filter(District != "Total") %>%  
  mutate(District_living_quarter = State_living_quarter * Proportion) %>% 
  arrange(District) %>% 
  relocate(Year, .before = State)


####################################
############## Part 2 ##############
####################################

# Forecast Selangor district no. of living quarters at latest year

############ Calculate Latest year (2025) Living Quarter Forecast ############

# Unique districts list
districts_list <- unique(district_living_quarters$District)

# Store forecast & accuracy results
forecast_output <- data.frame()
accuracy_output <- data.frame()

for (d in districts_list) {
  
  # Subset and sort data
  df <- district_living_quarters %>%
    filter(District == d) %>%
    arrange(Year)
  
  # Check enough data
  if (nrow(df) < 11) next
  
  # Create ts object
  ts_data <- ts(df$District_living_quarter, start = 2010, frequency = 1)
  
  # Train-test split
  train <- window(ts_data, start = 2010, end = 2017)
  test  <- window(ts_data, start = 2018, end = 2020)
  
  # Fit model on train
  model_train <- tslm(train ~ trend)
  forecast_test <- forecast(model_train, h = length(test))
  
  # Accuracy check
  acc <- accuracy(forecast_test, test)
  acc_df <- data.frame(District = d, RMSE = acc["Test set", "RMSE"], MAE = acc["Test set", "MAE"])
  accuracy_output <- rbind(accuracy_output, acc_df)
  
  # Forecast full model 2021–2025
  full_model <- tslm(ts_data ~ trend)
  forecast_future <- forecast(full_model, h = 5)
  
  # Add forecast values to output
  years <- 2021:2025
  values <- as.numeric(forecast_future$mean)
  forecast_df <- data.frame(District = d, Year = years, Forecast_LQ = values)
  forecast_output <- rbind(forecast_output, forecast_df)}

# Forecast 2021–2025
print(forecast_output)

# Model Accuracy (2018–2020)
print(accuracy_output)

############ Plot Forecast Graph ############

# Combine actual and forecasted data
historical_living_quarter <- district_living_quarters %>%
  select(District, Year, District_living_quarter) %>%
  mutate(Type = "Actual")
forecast_living_quarter <- forecast_output %>%
  dplyr::rename(District_living_quarter = Forecast_LQ) %>%
  mutate(Type = "Forecast")
combined_living_quarter <- bind_rows(historical_living_quarter, forecast_living_quarter)

# Plot all districts on one graph
ggplot(combined_living_quarter, aes(x = Year, 
                                    y = District_living_quarter, 
                                    color = District, 
                                    linetype = Type)) +
  geom_line(size = 1) +
  geom_point(size = 1) +
  labs(title = "Selangor District Living Quarters (2010–2025)",
       x = "Year", y = "Number of Living Quarters") +
  scale_y_continuous(labels = comma) +   # 👈 fix y-axis here
  theme_minimal() +
  theme(legend.position = "right")

####################################
############## Part 3 ##############
####################################

state_terraced_price <- terraced_price %>%
  pivot_longer(cols = starts_with("20"),
               names_to = "Year",
               values_to = "Price") %>% 
  mutate(Quarter = substr(Year, 7,8), 
         Year = substr(Year, 1,4))

# Tarraced price = cost of construction 
selangor_terraced_price = state_terraced_price %>% 
  dplyr::rename(District = `District/ Region`) %>% 
  # only take price as at start of the year
  # filter Selangor
  filter(Quarter == 1, 
         State == "Selangor") %>% 
  dplyr::rename(Ave_Unit_Price_Q1 = Price) %>% 
  select(-c(Quarter)) %>% 
  mutate(Year = as.numeric(Year))

Exposure_Table = combined_living_quarter %>% 
  left_join(selangor_terraced_price, by = c("District", "Year")) %>% 
  filter(Year >= 2019, 
         !District %in% c("Hulu Selangor", "Kuala Langat", "Sabak Bernam")) %>%
  mutate(Est_B40_Ave_Price_Q1 = Ave_Unit_Price_Q1 * 0.7, 
         Est_Insured_Unit = District_living_quarter * 0.15) %>% 
  select(State, District, Year, District_living_quarter, Est_Insured_Unit, 
         Ave_Unit_Price_Q1, Est_B40_Ave_Price_Q1) %>% 
  arrange(State, District, Year) 

############################## Write Table #############################
write_csv(Exposure_Table, "../Data/R_output/Exposure_Table.csv")

rm(acc, acc_df, df, model_train, full_model, forecast_df, forecast_test, forecast_future,
   forecast_output, district_living_quarters, forecast_living_quarter, historical_living_quarter, 
   residence_stock, terraced_price, selangor_terraced_price)
