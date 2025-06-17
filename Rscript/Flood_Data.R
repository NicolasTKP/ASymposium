Data = readxl::read_excel("../Data/Archive/IDMC_GIDD_Disasters_Internal_Displacement_Data.xlsx")
names(Data) <- gsub(" ", "_", names(Data))

###############################################################################
####################             Data Cleaning             ####################
###############################################################################

Flood_Data = Data %>% 
  filter(Hazard_Type == "Flood", 
         # Data before 2016 is not accurate & reliable
         Year > 2015) %>% 
  select(-c("ISO3", "Country_/_Territory", "Event_Codes_(Code:Type)")) %>% 
  mutate(Event_Name = tolower(Event_Name), 
         Event_Name = str_replace_all(Event_Name, "pulau pinang", "penang"), 
         Event_Name = str_replace_all(Event_Name, "malacca", "melaka"), 
         Event_Name = str_replace_all(Event_Name, "terrengganu", "terengganu"))

states = tolower(state_list) %>% 
  paste(collapse = "|") %>% 
  print()

# Extract matched state names (can match multiple if needed)
Flood_Data_State <- Flood_Data %>%
  mutate(State = str_extract_all(Event_Name, states), 
         State = sapply(State, 
                        function(x) if (length(x) > 0) paste(x, collapse = ", ") 
                        else NA), 
         
         # Specific location mapped to State
         State = case_when(str_detect(Event_Name, "beaufort|kota belud") ~ "sabah", 
                           str_detect(Event_Name, "bintulu") ~ "sarawak", 
                           str_detect(Event_Name, c("cameron highland|bentong|temerloh|raub")) ~ "pahang", 
                           str_detect(Event_Name, "gombak") ~ "selangor", 
                           str_detect(Event_Name, "baling") ~ "kedah", 
                           str_detect(Event_Name, "ipoh") ~ "perak", 
                           str_detect(Event_Name, "batu pabat|pontian") ~ "johor", 
                           TRUE ~ State), 
         
         # Filled in State based on Flood Date (After Research)
         State = case_when(Event_Name == "malaysia: flood - 10 states - 16/12/2021" ~ 
                                         "selangor, pahang, kelantan, terengganu, negeri sembilan, 
                                          melaka, perak, johor, sabah, kuala lumpur", 
                           Event_Name == "malaysia: flood - 8 states - 29/10/2021" ~ 
                                         "selangor, johor, sarawak, sabah, kelantan, perak, kedah, penang", 
                           Event_Name == "malaysia: flood - 6 states - 21/10/2021" ~ 
                                         "sarawak, sabah, johor, selangor, perak, negeri sembilan", 
                           Event_Name == "malaysia: flood - 6 states - 16/08/2021" ~ 
                                         "kedah, perak, selangor, johor, negeri sembilan, melaka", 
                           Event_Name == "malaysia: flood - 5 states - 19/11/2021" ~
                                         "selangor, perak, kedah, melaka, johor", 
                           Event_Name == "malaysia: floods - multiple states - 01/02/2016 (1st wave)" ~
                                         "kelantan, terengganu, pahang, johor, sabah, sarawak, kedah, perak", 
                           Event_Name == "malaysia: floods - multiple locations - 27/02/2016" ~
                                         "sarawak, johor, sabah, perak, selangor", 
                           Event_Name == "malaysia: floods - country-wide - 20/01/2017" ~
                                         "johor, kelantan, pahang, perak, selangor, sabah", 
                           Event_Name == "malaysia: east coast monsoon - 26/12/2016" ~
                                         "sarawak, johor, sabah, perak, selangor", 
                           Event_Name == "malaysia: flood - 01/01/2011" ~
                                         "kelantan, terengganu, pahang", 
                           TRUE ~ State)) 

# Check: 7 missing state
#check = Flood_Data_State %>% select(Event_Name, State) %>% filter(is.na((State))) 

###############################################################################
####################              Summarised               ####################
###############################################################################
Flood_Data_Final = Flood_Data_State %>% 
  select(Event_ID, Year, 'Date_of_Event_(start)', State, 
         Disaster_Internal_Displacements, Displacement_occurred) %>% 
  arrange('Date_of_Event_(start)', descending = T)

Flood_Data_Summary = Flood_Data_Final %>% 
