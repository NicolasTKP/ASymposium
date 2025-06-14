import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from joblib import dump, load
from keras.saving import register_keras_serializable
from keras.models import load_model
import tensorflow as tf
import tensorflow.keras.backend as K

@register_keras_serializable()
def custom_loss_with_variance(y_true, y_pred):
    mse = tf.reduce_mean(tf.square(y_true - y_pred), axis=-1)  # normal MSE
    std = tf.math.reduce_std(y_pred, axis=-1)                  # output variance
    loss = mse - 0.1 * std                                     # reward variance slightly
    return loss

def predict_with_uncertainty(model, input_data, n_iter=5):
    predictions = np.array([
        model(input_data, training=True).numpy()  # Enable dropout during inference
        for _ in range(n_iter)
    ])
    mean_prediction = predictions.mean(axis=0)
    std_prediction = predictions.std(axis=0)
    return mean_prediction, std_prediction

def create_sequences(input_data, n_steps):
    input_data = np.array(input_data)
    
    if len(input_data) >= n_steps:
        seq_x = input_data[-n_steps:, :]
        return np.array([seq_x])
    else:
        raise ValueError(f"Input data has fewer rows ({len(input_data)}) than n_steps ({n_steps})")

model = load_model('Model/daily_wl_model.keras', custom_objects={
    'custom_loss_with_variance': custom_loss_with_variance
})

# import data
df = pd.read_csv('Data/cleaned_klangWLRF.csv', parse_dates=["datetime"], index_col="datetime")
df.index = pd.to_datetime(df.index, format='mixed')
df['date_only'] = df.index.date
max_wl_per_day = df.loc[df.groupby('date_only')['wl'].idxmax()]
df = max_wl_per_day.drop(columns='date_only')

rfT = df.reset_index().pivot_table(index='datetime', columns='station_id', values='rfdaily')
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
scaler = load('daily_scaler.save')
combined_data = pd.concat([rfT, wlT], axis=1)
#combined_data = combined_data[combined_data.index.astype(str).str.len() == 10] # optional: convert the data to daily based
scaled_data = scaler.transform(combined_data)
# convert the numpy arrays back to df
columns = rfT.columns.tolist() + wlT.columns.tolist()
input_df = pd.DataFrame(scaled_data, columns=columns)
rfTP = rfT.add_suffix('_prob')
wlTP = wlT.add_suffix('_prob')
prob_columns = rfTP.columns.tolist() + wlTP.columns.tolist()

# Define the number of steps for prediction
n_steps = 12  # days

# Define the ppredicted df to insert the predicted values
predicted_df = input_df.tail(n_steps)
print(predicted_df)
prob_df = pd.DataFrame(columns=prob_columns)

for i in range(365):  # Predict one year ahead
    # Define the input data for prediction
    input_data = create_sequences(predicted_df, n_steps=n_steps)

    # Predict the values using the model
    predicted_value = model.predict(input_data)
    predicted_value += np.random.normal(0, 0.02, predicted_value.shape)
    #predicted_value, uncertainty = predict_with_uncertainty(model, input_data)
    #print(f"Uncertainty: {uncertainty}")
    #tmp_prob_df = pd.DataFrame(uncertainty, columns=prob_columns)
    temp_df = pd.DataFrame(predicted_value, columns=columns)
    predicted_df = pd.concat([predicted_df, temp_df], axis=0)
    #prob_df = pd.concat([prob_df, tmp_prob_df], axis=0)

reversed_data = scaler.inverse_transform(predicted_df)
reversed_df = pd.DataFrame(reversed_data, columns=columns)
reversed_df = reversed_df.iloc[n_steps:]
print(reversed_df)
#reversed_df = reversed_df.reset_index(drop=True)
#prob_df = prob_df.reset_index(drop=True)
#reversed_df = pd.concat([reversed_df, prob_df], axis=1)
#print(reversed_df)
# Save the predicted values to a CSV file
reversed_df.to_csv('Data/predicted_klangWLRF.csv', index=False)

