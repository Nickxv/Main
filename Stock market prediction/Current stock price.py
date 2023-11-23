import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests

class StockPriceViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Price Viewer")

        self.symbol_label = ttk.Label(root, text="Enter Stock Symbol:")
        self.symbol_label.grid(row=0, column=0, padx=10, pady=10)

        self.symbol_entry = ttk.Entry(root)
        self.symbol_entry.grid(row=0, column=1, padx=10, pady=10)

        self.fetch_button = ttk.Button(root, text="Fetch Stock Price", command=self.fetch_stock_price)
        self.fetch_button.grid(row=0, column=2, padx=10, pady=10)

        self.price_label = ttk.Label(root, text="Stock Price: ")
        self.price_label.grid(row=1, column=0, columnspan=3, pady=10)

    def fetch_stock_price(self):
        api_key = "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"  # Replace with your Alpha Vantage API key
        symbol = self.symbol_entry.get().upper()
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"

        try:
            response = requests.get(url)
            data = response.json()
            price = data['Global Quote']['05. price']
            self.price_label.config(text=f"Stock Price: {price}")
        except Exception as e:
            self.price_label.config(text="Error fetching stock price.")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockPriceViewer(root)
    root.mainloop()

    