import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input, Dropout, LayerNormalization
from joblib import dump, load
from sklearn.metrics import mean_squared_error, r2_score

# Function to extract the data into an array of sequences. Eg: (if n_steps=20, y = row 20)
def create_sequences(input_data, n_steps, n_ahead=1):
    X, y = [], []
    for i in range(len(input_data) - n_steps - n_ahead + 1):
        end_ix = i + n_steps
        seq_x = input_data[i:end_ix, :]  # All columns
        seq_y = input_data[end_ix, :]   # All columns
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)


# import data
df = pd.read_csv('Data/cleaned_klangWLRF.csv', parse_dates=["datetime"], index_col="datetime")
rfT = df.reset_index().pivot_table(index='datetime', columns='station_id', values='rfdaily') # rf if hourly, rfdaily if daily
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
combined_data = combined_data[combined_data.index.astype(str).str.len() == 10] # optional: convert the data to daily based
print(combined_data)
print(combined_data.shape)
scaled_data = scaler.fit_transform(combined_data)
dump(scaler, 'daily_scaler.save')

# split 70% data for training, 20% for validate, 10% for testing
total_samples = len(scaled_data)
train_end = int(total_samples * 0.7)
validation_end = int(total_samples * 0.9)
train_data = scaled_data[:train_end]
validation_data = scaled_data[train_end:validation_end]
testing_data = scaled_data[validation_end:]


# convert the numpy arrays back to df
columns = [rfT.columns.tolist() + wlT.columns.tolist()]
train_df = pd.DataFrame(train_data, columns=columns)
validation_df = pd.DataFrame(validation_data, columns=columns)
testing_df = pd.DataFrame(testing_data, columns=columns)

# check for the data stats
stats_train = train_df.describe().loc[['mean', 'std', 'min', 'max']]
stats_validation = validation_df.describe().loc[['mean', 'std', 'min', 'max']]
stats_testing = testing_df.describe().loc[['mean', 'std', 'min', 'max']]
print("Training Data Stats:\n", stats_train, "\n")
print("Validation Data Stats:\n", stats_validation, "\n")
print("Testing Data Stats:\n", stats_testing, "\n")

# create training data with the sequences function
X_train, y_train = create_sequences(train_data, n_steps=7) # 7 days
X_validation, y_validation = create_sequences(validation_data, n_steps=7) # 7 days
X_test, y_test = create_sequences(testing_data, n_steps=7) # 7 days
print("Training data shape:", X_train.shape, y_train.shape)
print("Validation data shape:", X_validation.shape, y_validation.shape)
print("Testing data shape:", X_test.shape, y_test.shape)

def training():
    # Build the LSTM model
    model = Sequential([
        Input(shape=(7, 6)), # shape = 168 hours, 6 features (rf and wl for 3 stations each)
        LSTM(128, return_sequences=True, dropout=0.2, recurrent_dropout=0.2),     # Return full sequence for next LSTM
        LayerNormalization(),
        LSTM(64, return_sequences=False, dropout=0.2, recurrent_dropout=0.2),     # Return final output only
        LayerNormalization(),
        Dense(64, activation='relu'),
        Dense(6, activation='linear')  # Output layer for 6 features (rf and wl)
    ])

    model.compile(optimizer='adam', loss='mae', metrics=['mae'])


    # Train the model & save the model and training history
    history = model.fit(
        X_train, y_train,
        epochs=30,
        batch_size=32,
        validation_data=(X_validation, y_validation)
    )
    dump(model, 'Model/daily_wl_model.keras')
    dump(history, 'Model/daily_model_history.joblib')

def evaluation():
    global X_train, y_train, X_validation, y_validation, X_test, y_test, scaler
    # Load the model and history
    model = load('Model/daily_wl_model.keras')
    history = load('Model/daily_model_history.joblib')

    # Plot the training and validation loss
    plt.figure(figsize=(10, 6))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Training History')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.show()

    train_pred = model.predict(X_train)
    validation_pred = model.predict(X_validation)
    test_pred = model.predict(X_test)
    y_train = scaler.inverse_transform(y_train)
    y_validation = scaler.inverse_transform(y_validation)
    y_test = scaler.inverse_transform(y_test)
    train_pred = scaler.inverse_transform(train_pred)
    validation_pred = scaler.inverse_transform(validation_pred) 
    test_pred = scaler.inverse_transform(test_pred)
    print("MSE:", mean_squared_error(y_test, test_pred))
    print("R² Score:", r2_score(y_test, test_pred))
    test_loss = model.evaluate(X_test, y_test)
    print("Test Loss:", test_loss)
    print("Train Loss:", model.evaluate(X_train, y_train))
    plot_predictions_with_error(y_train, train_pred, 'Training Data: True vs Predicted')
    plot_predictions_with_error(y_validation, validation_pred, 'Validation Data: True vs Predicted')
    plot_predictions_with_error(y_test, test_pred, 'Test Data: True vs Predicted')
    

def plot_predictions_with_error(true_data, predicted_data, title):
    plt.figure(figsize=(10, 12))
    
    # Flatten arrays to ensure compatibility with matplotlib
    true_data_flatten = true_data.flatten()
    predicted_data_flatten = predicted_data.flatten()
    
    # Calculate error
    error = true_data_flatten - predicted_data_flatten
    positive_error_std = np.std(error[error >= 0])
    negative_error_std = np.std(error[error < 0])
    
    # Plot true data vs. predicted data
    ax1 = plt.subplot(2, 1, 1)  # 2 rows, 1 column, 1st subplot
    ax1.plot(true_data_flatten, label='True Data')
    ax1.plot(predicted_data_flatten, label='Predicted Data', alpha=0.7)
    ax1.set_title(title)
    ax1.set_ylabel('Value')
    ax1.legend()
    plt.show()



if __name__ == "__main__":
    training()
    evaluation()
    