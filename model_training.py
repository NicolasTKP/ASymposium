import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('Data/cleaned_klangWLRF.csv', parse_dates=["datetime"], index_col="datetime")

RfT = df.reset_index().pivot_table(index='datetime', columns='station_id', values='rf')
RfT = RfT.sort_index() 
# print(RfT)
print(RfT.isna().sum())
print(RfT.isna().sum().sum())
print(RfT[RfT.isna().any(axis=1)])