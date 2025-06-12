import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input

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

# validate data
print(rfT.isna().sum())
print(rfT.isna().sum().sum())
print(rfT[rfT.isna().any(axis=1)])
print(wlT.isna().sum())
print(wlT.isna().sum().sum())
print(wlT[wlT.isna().any(axis=1)])


# scare the data within the range of 0 to 1, and convert the data to numpy array
scaler = MinMaxScaler()
combined_data = pd.concat([rfT, wlT], axis=1)
scaled_data = scaler.fit_transform(combined_data)


# split 70% data for training, 20% for validate, 10% for testing
total_samples = len(scaled_data)
train_end = int(total_samples * 0.7)
validation_end = int(total_samples * 0.9)
train_data = scaled_data[:train_end]
validation_data = scaled_data[train_end:validation_end]
test_data = scaled_data[validation_end:]


# convert the numpy arrays back to df
columns = [rfT.columns.tolist() + wlT.columns.tolist()]
train_df = pd.DataFrame(train_data, columns=columns)
validation_df = pd.DataFrame(validation_data, columns=columns)
test_df = pd.DataFrame(test_data, columns=columns)

# check for the data stats
stats_train = train_df.describe().loc[['mean', 'std', 'min', 'max']]
stats_validation = validation_df.describe().loc[['mean', 'std', 'min', 'max']]
stats_test = test_df.describe().loc[['mean', 'std', 'min', 'max']]
print("Training Data Stats:\n", stats_train, "\n")
print("Validation Data Stats:\n", stats_validation, "\n")
print("Testing Data Stats:\n", stats_test, "\n")

# Function to extract the data into an array of sequences. Eg: (x = row 0-19 if n_steps=20, y = row 20)
def create_sequences(input_data, n_steps, n_ahead=1):
    X, y = [], []
    for i in range(len(input_data) - n_steps - n_ahead + 1):
        end_ix = i + n_steps
        seq_x = input_data[i:end_ix, :]  # All columns
        seq_y = input_data[end_ix, 10:20]   # Target WL, one step ahead, columns 11-20 (10-19 in 0-indexed)
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)

# create training data with the sequences function
X_train, y_train = create_sequences(train_data, n_steps=20)
X_validation, y_validation = create_sequences(validation_data, n_steps=20)
X_test, y_test = create_sequences(test_data, n_steps=20)
print("Training data shape:", X_train.shape, y_train.shape)


# Build the LSTM model
model = Sequential([
    Input(shape=(20, 20)),
    LSTM(64, activation='relu'),  # '20' represents the number of features in each time step
    Dense(10)
])

# Optional to include a second LSTM layer
# model = Sequential([
#     LSTM(64, return_sequences=True, input_shape=(20, 20)),
#     LSTM(32),
#     Dense(32, activation='relu'),
#     Dense(10)
# ])

model.compile(optimizer='adam', loss='mse')


# Train the model
history = model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=32,
    validation_data=(X_validation, y_validation)
)