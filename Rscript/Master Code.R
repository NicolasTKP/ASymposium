library(stringr)
library(dplyr)
library(tidyverse)
library(openexcel)
library(readxl)
library(forecast)
library(ggplot2)
library(scales)  # for comma()
library(mice)
library(plyr)
library(rlang)

###############################################################################
####################                Control                ####################
###############################################################################
# Create Path
HackathonPath = str_c("./")
ReferencePath = str_c(HackathonPath, "/Reference") 
OutputFile = str_c(HackathonPath, "/R_Output") 
WorkingPath = str_c(HackathonPath, "/R_Code")

###############################################################################
####################                Part 1                 ####################
###############################################################################

setwd(WorkingPath)
source("RFCleaning.R")
source("CombineWLRF.R")

rm(completed_data, imputed, klangRF, klangWL, klangWL2, selected_cols)

###############################################################################
####################                Part 2                 ####################
###############################################################################

### PREMIUM INPUT ###
ExpenseRatio = 0.15
RiskMargin = 0.1
ProfitMargin = 0.1
ReinsuranceCost = 0.3

# To calculate EAD
source("Exposure.R")
source("EADnPremium.R")

  ## Calculate estimation proportion of each state residence property among whole Selangor
  # # Calculate Selangor district no. of living quarters year by year
# Forecast Selangor district no. of living quarters at latest year
# Forecast to get 2025 klang living quarters

