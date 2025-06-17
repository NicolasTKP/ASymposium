Exposure_Table <- read_csv("../Data/R_output/Exposure_Table.csv")

############################## Example State #############################
# Rate for damage ratio
BaseRatio = 0.032
k = 0.5
m = 0.4

### Klang ###
Klang_Exposure = Exposure_Table %>% 
  filter(District == "Klang", 
         Year == 2025)

############################## 3 Example Station #############################

# Choose 3 station as example
klang_loss <- cbind(Klang_Exposure, klang_WL_probability) %>%
  filter(Station_ID %in% c("3014080_", "SELATMUARA", "PEKANMERU")) %>%
  
  pivot_longer(cols = starts_with("P(X"),                 
               names_to = "WL_Damage_Threshold_Multiplier",                    
               values_to = "Probability_WL") %>% 
  mutate(WL_Damage_Threshold_Multiplier = as.numeric(
           str_extract(WL_Damage_Threshold_Multiplier, "\\d+\\.\\d+"))) %>% 
           
  # Add Water level duration (in days) column
  slice(rep(1:n(), each = 4)) %>%
  mutate(WL_Duration = rep(1:4, times = nrow(.) / 4)) %>% 
  
  
  mutate(
    # Calculate damage ratio for each prob. tier
    Ave_WL_Duration = 2,
    Ave_WL_Damage_Threshold_Multiplier = mean(WL_Damage_Threshold_Multiplier), 
    Damage_Ratio = (
      BaseRatio * (WL_Duration/ Ave_WL_Duration)^k * 
        (WL_Damage_Threshold_Multiplier/Ave_WL_Damage_Threshold_Multiplier)^m), 
    
    # Calculate total asset at risk
    Est_AssetAtRisk = Est_Insured_Unit * Est_B40_Ave_Price_Q1, 
    EAL = Est_AssetAtRisk * Damage_Ratio * Probability_WL, 
    EAL_per_POLHDR = Est_B40_Ave_Price_Q1 *  Damage_Ratio * Probability_WL) %>% 
  mutate(Probability_WL = round(Probability_WL,8), 
         EAL = round(as.numeric(format(EAL,4), scientific = F),2), 
         EAL_per_POLHDR = round(as.numeric(format(EAL_per_POLHDR,4), scientific = F),2)) %>% 
  
  select(-c(State, District, Year)) %>% 
  relocate(.before = District_living_quarter, Station_ID:Station_Name)

############################## EAD for each Station #############################
Expected_Loss <- aggregate(
  cbind(EAL, EAL_per_POLHDR) ~ Station_ID + Station_Name + `Risk Level`,
  data = klang_loss,
  FUN = sum,
  na.rm = TRUE
)

############################## Premium #############################

### Colname ###
TotalLoading = sum(ExpenseRatio, RiskMargin, ProfitMargin, ReinsuranceCost)

Loading = Expected_Loss %>% 
  select(-c(`Risk Level`, EAL)) %>% 
  mutate('Expense Ratio (15%)' = round(ExpenseRatio * EAL_per_POLHDR, 2),
         'Risk Margin (10%)'     = round(RiskMargin  * EAL_per_POLHDR, 2),
         'Profit Margin (10%)'   = round(ProfitMargin * EAL_per_POLHDR, 2),
         'Reinsurance Cost (30%)'   = round(ReinsuranceCost * EAL_per_POLHDR, 2),
         'Gross Premium (RM)' = round(EAL_per_POLHDR * (1 + TotalLoading), 2), 
         'Monthly Payment (RM)' =  round(`Gross Premium (RM)` / 12, 2))


############################## Write Table #############################
write_csv(klang_loss, "../Data/R_output/Klang_Loss_Table_2025.csv")



