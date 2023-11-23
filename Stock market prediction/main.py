import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import yfinance as yf
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StockPredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Market Prediction")
        self.root.geometry("800x600")

        self.symbol_label = ttk.Label(root, text="Stock Symbol:")
        self.symbol_label.pack(pady=10)
        self.symbol_entry = ttk.Entry(root)
        self.symbol_entry.pack(pady=10)

        self.predict_button = ttk.Button(root, text="Predict", command=self.predict_stock)
        self.predict_button.pack(pady=10)

        self.result_label = ttk.Label(root, text="")
        self.result_label.pack(pady=10)

        self.plot_button = ttk.Button(root, text="Plot Historical Data", command=self.plot_data)
        self.plot_button.pack(pady=10)

    def fetch_stock_data(self, symbol):
        try:
            # Fetch data up to today
            end_date = pd.Timestamp.today().strftime('%Y-%m-%d')
            stock_data = yf.download(symbol, start="2022-01-01", end=end_date)
            return stock_data
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {str(e)}")
            return None

    def train_model(self, data):
        data['Date'] = data.index
        data['Date'] = pd.to_datetime(data['Date'])
        data['Date'] = data['Date'].map(pd.Timestamp.timestamp)

        X = data[['Date']]
        y = data['Close']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        print(f'Mean Squared Error: {mse}')

        # Save the model and scaler
        joblib.dump(model, 'model.pkl')
        print("Model saved as model.pkl")

        return model

    def predict_stock(self):
        symbol = self.symbol_entry.get().upper()
        if not symbol:
            messagebox.showwarning("Warning", "Please enter a stock symbol.")
            return

        data = self.fetch_stock_data(symbol)
        if data is not None and not data.empty:
            model = self.train_model(data)
            if model:
                # Predict the closing price for the last date in the dataset
                last_date = data.index[-1]
                last_date_timestamp = pd.Timestamp.timestamp(last_date)
                prediction = model.predict([[last_date_timestamp]])
                self.result_label.config(text=f"Predicted Closing Price: {round(prediction[0], 2)}")
        else:
            self.result_label.config(text="")

    def plot_data(self):
        symbol = self.symbol_entry.get().upper()
        if not symbol:
            messagebox.showwarning("Warning", "Please enter a stock symbol.")
            return

        data = self.fetch_stock_data(symbol)
        if data is not None and not data.empty:
            figure, ax = plt.subplots(figsize=(8, 4))
            ax.plot(data.index, data['Close'], label='Actual Closing Price')
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.6)

            ax.set_title(f'{symbol} Stock Price')
            ax.set_xlabel('Date')
            ax.set_ylabel('Closing Price')
            ax.legend()

            canvas = FigureCanvasTkAgg(figure, master=self.root)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            canvas.draw()
        else:
            messagebox.showerror("Error", "Failed to fetch data.")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockPredictionApp(root)
    root.mainloop()
    
    # ... (previous code)

    def train_model(self, data):
        data['Date'] = data.index
        data['Date'] = pd.to_datetime(data['Date'])
        data['Date'] = data['Date'].map(pd.Timestamp.timestamp)

        X = data[['Date']]
        y = data['Close']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        print(f'Mean Squared Error: {mse}')

        # Save the model
        joblib.dump(model, 'model.pkl')
        print("Model saved as model.pkl")

        return model

# ... (remaining code)
    # ... (previous code)
from sklearn.preprocessing import StandardScaler

class StockPredictionApp:
    # ... (previous code)

    def train_model(self, data):
        data['Date'] = data.index
        data['Date'] = pd.to_datetime(data['Date'])
        data['Date'] = data['Date'].map(pd.Timestamp.timestamp)

        X = data[['Date']]
        y = data['Close']

        # Standardize features by removing the mean and scaling to unit variance
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        print(f'Mean Squared Error: {mse}')

        # Save the model and scaler
        joblib.dump(model, 'model.pkl')
        print("Model saved as model.pkl")
        joblib.dump(scaler, 'scaler.pkl')
        print("Scaler saved as scaler.pkl")

        return model

# ... (remaining code)
    # ... (previous code)

    def predict_stock(self):
        symbol = self.symbol_entry.get().upper()
        if not symbol:
            messagebox.showwarning("Warning", "Please enter a stock symbol.")
            return

        data = self.fetch_stock_data(symbol)
        if data is not None and not data.empty:
            # Load the model and scaler
            model = joblib.load('model.pkl')
            scaler = joblib.load('scaler.pkl')

            # Preprocess the input data
            last_date = data.index[-1]
            last_date_timestamp = pd.Timestamp.timestamp(last_date)
            input_data = scaler.transform([[last_date_timestamp]])

            # Predict the closing price
            prediction = model.predict(input_data)
            self.result_label.config(text=f"Predicted Closing Price: {round(prediction[0], 2)}")
        else:
            self.result_label.config(text="")

