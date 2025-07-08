import pandas as pd
import os

if os.path.exists('klangRF.csv') and os.path.getsize('klangRF.csv') > 0:
    df = pd.read_csv('klangRF.csv')
else:
    df = pd.DataFrame()

print("Initial DataFrame loaded with shape:\n", df)

df = df[df['station_id'] == '27869']

df.to_csv('klangRF.csv', index=False)