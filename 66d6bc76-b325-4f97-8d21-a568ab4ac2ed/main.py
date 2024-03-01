from surmount.base_class import Strategy, TargetAllocation
#from surmount.data import OHLCV
from surmount.technical_indicators import SMA
import pandas as pd

class TradingStrategy(Strategy):
    def __init__(self):
        # Define pairs of stocks, where the first is in the S&P 500 and the second isn't
        self.stock_pairs = [
            ('AAPL', 'CRUS'), ('MSFT', 'MDB'), ('AMZN', 'ETSY'), ('MSFT', 'ADBE'), ('GOOGL', 'YHOO'), ('MSFT', 'DDOG'), ('JPM', 'TFC'), ('WMT', 'KR'), ('PG', 'KMB'), ('MCD', 'DPZ'), ('BA', 'SAVE'), ('UNH', 'HUM'), ('XOM', 'COP'), ('DIS', 'ROKU'), ('LLY', 'MRNA'), ('FB', 'PINS'), ('VZ', 'TMUS'), ('NVDA', 'AMD'), ('PFE', ' BIIB'), ('INTC', 'MRVL'), ('KO', 'MNST'), ('JNJ', 'MDT'), ('V', 'PYPL'), ('COST', 'BJ')
        ]
        # Historical price movement window in days
        self.history_window = 90
        # Relative divergence threshold to identify buying opportunity
        self.divergence_threshold = 0.05
        # Holding period in days
        self.holding_period = 7
        
        # Data requirement for each stock in pair
        self.data_list = []
        for pair in self.stock_pairs:
            for stock in pair:
                self.data_list.append(OHLCV(stock))
    
    @property
    def interval(self):
        return "1day"
    
    @property
    def assets(self):
        # Return a list of unique stocks from pairs
        stocks = set([stock for pair in self.stock_pairs for stock in pair])
        return list(stocks)
    
    @property
    def data(self):
        return self.data_list
    
    def run(self, data):
        # Initialize allocation dict
        allocation_dict = {stock: 0 for stock in self.assets}
        # Iterate through each stock pair
        for sp500_stock, non_sp500_stock in self.stock_pairs:
            sp500_data = data['ohlcv'][sp500_stock]
            non_sp500_data = data['ohlcv'][non_sp500_stock]
            # Calculate the Simple Moving Average (SMA) for the history window for both stocks
            sp500_sma = SMA(sp500_stock, sp500_data, self.history_window)
            non_sp500_sma = SMA(non_sp500_stock, non_sp500_data, self.history_window)
            # Calculate the current price for both stocks
            sp500_current_price = sp500_data[-1]['close']
            non_sp500_current_price = non_sp500_data[-1]['close']
            # Check for similar price movement using SMA and then check divergence
            if sp500_sma and non_sp500_sma:
                sp500_sma_latest = sp500_sma[-1]
                non_sp500_sma_latest = non_sp500_sma[-1]
                divergence = abs(sp500_sma_latest - non_sp500_sma_latest) / sp500_sma_latest
                if divergence > self.divergence_threshold:
                    # Invest in the lower priced stock of the pair
                    if sp500_current_price < non_sp500_current_price:
                        allocation_dict[sp500_stock] += 0.01  # 1% bankroll investment
                    else:
                        allocation_dict[non_sp500_stock] += 0.01  # 1% bankroll investment
        # Adjust allocations to remain within the 0 to 1 (inclusive) range if necessary
        total_allocation = sum(allocation_dict.values())
        if total_allocation > 1:
            allocation_dict = {k: v / total_allocation for k, v in allocation_dict.items()}
        return TargetAllocation(allocation_dict)