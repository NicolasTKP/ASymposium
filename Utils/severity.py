import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

ori_df = pd.read_csv('../Data/R_output/cleaned_klangWLRF.csv')
predict_df = pd.read_csv('../Data/Py_output/predicted_klangWLRF.csv')

# Select columns 0 to 6
columns_to_plot = predict_df.columns[1:]

# Plot each column
plt.figure(figsize=(12, 6))
for col in columns_to_plot:
    plt.plot(predict_df[col], label=col)

plt.title('Predicted Values (Columns 0 to 6)')
plt.xlabel('Time Step (Days)')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

danger_dic = {
    '27234': 4.0,
    '3014080_': 3.0,
    'PANDAMARAN': 2.2,
    'SELATMUARA': 3.0
}

df = pd.DataFrame(columns=['Station', 'Station Name','Danger Level', 'Exceedance Count', 'Exceedance Count (1.1x)', 'Exceedance Count (1.2x)', 'Exceedance Count (1.3x)', '2-Day Danger Exceedance Count'])

for station in danger_dic:
    danger_level = danger_dic[station]
    key_index = list(danger_dic.keys()).index(station)
    column_name = predict_df.columns[key_index+4]
    column = predict_df[column_name]
    count = (column > danger_level).sum()
    new_row = pd.DataFrame([{'Station': station, 'Station Name': ori_df.loc[ori_df['station_id'] == station, 'station_name'].values[0], 'Danger Level': danger_level, 'Exceedance Count': count}])
    df = pd.concat([df, new_row], ignore_index=True)
    count = (column > danger_level*1.1).sum()
    df.at[df.index[-1], 'Exceedance Count (1.1x)'] = count
    count = (column > danger_level*1.2).sum()
    df.at[df.index[-1], 'Exceedance Count (1.2x)'] = count
    count = (column > danger_level*1.3).sum()
    df.at[df.index[-1], 'Exceedance Count (1.3x)'] = count

    above_danger = (column > danger_level).values

    count = 0
    i = 0
    while i < len(above_danger) - 1:
        if above_danger[i] and above_danger[i + 1]:
            count += 1
            i += 2  # skip the next day
        else:
            i += 1

    df.at[df.index[-1], '2-Day Danger Exceedance Count'] = count

print(df)
df.to_csv('../Data/Py_output/klang_flood_severity.csv', index=False)