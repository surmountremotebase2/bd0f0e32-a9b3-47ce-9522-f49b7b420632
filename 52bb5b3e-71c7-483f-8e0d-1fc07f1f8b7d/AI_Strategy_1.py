from surmount.base_class import Strategy, TargetAllocation
from surmount.data import Asset, OHLCV
from datetime import datetime, timedelta

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the tickers of interest
        self.tickers = ["AAPL", "GOOGL", "MSFT", "AMZN"]
        # Define a dictionary to track when stocks were bought
        self.buy_dates = {ticker: None for ticker in self.tickers}

    @property
    def interval(self):
        # Set data interval to daily
        return "1day"
    
    @property
    def assets(self):
        # List of assets the strategy will deal with
        return self.tickers

    @property
    def data(self):
        # Request OHLCV data for our assets
        return [OHLCV(ticker) for ticker in self.tickers]

    def run(self, data):
        # Get the current date from the latest data entry
        current_date = datetime.strptime(data["ohlcv"][-1][self.tickers[0]]["date"], "%Y-%m-%d")
        
        allocation_dict = {}
        for ticker in self.tickers:
            # Check if stock was bought and 7 days have passed
            if self.buy_dates[ticker] is not None and current_date >= self.buy_dates[ticker] + timedelta(days=7):
                # If 7 days passed, set allocation to 0 (sell)
                allocation_dict[ticker] = 0
                # Update buy_dates to None as the stock is sold
                self.buy_dates[ticker] = None
            else:
                # If not bought before or it hasn't been 7 days, maintain position (do nothing)
                # This assumes starting with no holdings, so we set allocation to 0
                # Update logic here if you start with initial holdings or use signals for buying
                allocation_dict[ticker] = 0 

            # Example buying logic - replace or add your condition to buy or modify the holding
            # Here we assume no buying strategy, ensure to integrate with checks if intending to buy
            # if <buy_condition>:
            #     allocation_dict[ticker] = <allocation_percentage>
            #     self.buy_dates[ticker] = current_date

        return TargetAllocation(allocation_dict)