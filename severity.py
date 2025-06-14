import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

ori_df = pd.read_csv('Data/normal_klangWLRF.csv')
predict_df = pd.read_csv('Data/predicted_normal_klangWLRF.csv')

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

for station in danger_dic:
    danger_level = danger_dic[station]
    key_index = list(danger_dic.keys()).index(station)
    column_name = predict_df.columns[key_index+4]
    column = predict_df[column_name]
    count = (column > danger_level).sum()
    print(f"Number of times {station} exceeds danger level {danger_level}: {count}")

for station in danger_dic:
    danger_level = danger_dic[station]
    key_index = list(danger_dic.keys()).index(station)
    column_name = predict_df.columns[key_index + 4]
    column = predict_df[column_name]

    above_danger = (column > danger_level).values

    count = 0
    i = 0
    while i < len(above_danger) - 1:
        if above_danger[i] and above_danger[i + 1]:
            count += 1
            i += 2  # skip the next day
        else:
            i += 1

    print(f"Number of 2-day danger exceedances for {station} (> {danger_level}): {count}")