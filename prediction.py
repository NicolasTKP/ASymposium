import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from joblib import dump, load

def create_sequences(input_data, n_steps=365):
    input_data = np.array(input_data)
    
    if len(input_data) >= n_steps:
        seq_x = input_data[-n_steps:, :]
        return np.array([seq_x])
    else:
        raise ValueError(f"Input data has fewer rows ({len(input_data)}) than n_steps ({n_steps})")

model = load('Model/wl_model.keras')

# import data
df = pd.read_csv('Data/cleaned_klangWLRF.csv', parse_dates=["datetime"], index_col="datetime")
rfT = df.reset_index().pivot_table(index='datetime', columns='station_id', values='rf')
rfT = rfT.sort_index() 
wlT = df.reset_index().pivot_table(index='datetime', columns='station_id', values='wl')
wlT = wlT.sort_index() 
rfT = rfT.add_prefix('rf_')
wlT = wlT.add_prefix('wl_')
# clean data with mode values
for col in rfT.columns:
    mode = rfT[col].mode()
    if not mode.empty:
        rfT[col].fillna(mode[0], inplace=True)
for col in wlT.columns:
    mode = wlT[col].mode()
    if not mode.empty:
        wlT[col].fillna(mode[0], inplace=True)
# scare the data within the range of 0 to 1, and convert the data to numpy array
scaler = load('scaler.save')
combined_data = pd.concat([rfT, wlT], axis=1)
scaled_data = scaler.transform(combined_data)
# convert the numpy arrays back to df
columns = [rfT.columns.tolist() + wlT.columns.tolist()]
input_df = pd.DataFrame(scaled_data, columns=columns)

# Define the number of steps for prediction
n_steps = 10  # hour

# Define the ppredicted df to insert the predicted values
predicted_df = input_df.tail(n_steps)

for i in range(n_steps):  # Predict one year ahead
    # Define the input data for prediction
    input_data = create_sequences(predicted_df, n_steps=n_steps)

    # Predict the values using the model
    predicted_value = model.predict(input_data)
    temp_df = pd.DataFrame(predicted_value, columns=columns)
    predicted_df = pd.concat([predicted_df, temp_df], axis=0)


reversed_data = scaler.inverse_transform(predicted_df)
reversed_df = pd.DataFrame(reversed_data, columns=columns)
reversed_df = reversed_df.iloc[n_steps:]
print(reversed_df)
# Save the predicted values to a CSV file
reversed_df.to_csv('Data/predicted_klangWLRF.csv', index=False)

