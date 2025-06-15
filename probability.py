import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('Data/predicted_klangWLRF.csv')
ori_df = pd.read_csv('Data/cleaned_klangWLRF.csv')
columns = df.columns[4:]

danger_dic = {
    'wl_27234': 4.0,
    'wl_3014080_': 3.0,
    'wl_PANDAMARAN': 2.2,
    'wl_SELATMUARA': 3.0
}
# danger_dic = {
#     'wl_PEKANMERU': 4.2
# }

prob_df = pd.DataFrame(columns=['Station_ID', 'Station_Name','P(X > Danger * 1.05)',
                           'P(X > Danger * 1.1)', 'P(X > Danger * 1.15)'])

for col in columns:
    data = df[col].values

    mean = np.mean(data)
    std = np.std(data)
    dangerLvl = danger_dic.get(col, 0)
    # Probability of exceeding danger level
    p_exceed = norm.sf(dangerLvl*1.05, loc=mean, scale=std)  # sf = 1 - cdf
    new_row = pd.DataFrame([{
        'Station_ID': col.replace('wl_', ''),
        'Station_Name': ori_df.loc[ori_df['station_id'] == col.replace('wl_', ''), 'station_name'].values[0],
        'P(X > Danger * 1.05)': round(p_exceed,50)
    }])
    prob_df = pd.concat([prob_df, new_row], ignore_index=True)
    p_exceed = norm.sf(dangerLvl*1.1, loc=mean, scale=std)
    prob_df.at[prob_df.index[-1], 'P(X > Danger * 1.1)'] = round(p_exceed, 50)
    p_exceed = norm.sf(dangerLvl*1.15, loc=mean, scale=std)
    prob_df.at[prob_df.index[-1], 'P(X > Danger * 1.15)'] = round(p_exceed, 50)

print(prob_df)
prob_df.to_csv('Data/probability_klangWLRF.csv', index=False)
# days = 365
# prob_at_least_once = 1 - (1 - p_exceed) ** days
# print(f"Chance of exceeding at least once in a year for {col}: {prob_at_least_once:.20f}")