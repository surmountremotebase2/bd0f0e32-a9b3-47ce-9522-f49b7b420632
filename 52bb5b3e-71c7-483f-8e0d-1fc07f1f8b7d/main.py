from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.logging import log
import pandas as pd

class TradingStrategy(Strategy):
    def __init__(self):
        # Pair of companies to compare. First is not in S&P 500, second is in S&P 500
        self.pairs = [("AMD", "INTC"), ("SQ", "V")]  # Example pairs
        # Keeping track of Simple Moving Averages to identify divergences
        self.data_list = []

    @property
    def assets(self):
        # Collects all unique tickers from pairs. Converts [[(pair1), (pair2)],...] to [ticker1, ticker2,...]
        return list(set([item for sublist in self.pairs for item in sublist]))

    @property
    def interval(self):
        # Daily intervals for checking longer-term alignment
        return "1day"

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation = {}
        
        for pair in self.pairs:
            non_sp_ticker, sp_ticker = pair
            try:
                # Calculate 20 days Simple Moving Average for both tickers
                sma_non_sp = SMA(non_sp_ticker, data["ohlcv"], 20)
                sma_sp = SMA(sp_ticker, data["ohlcv"], 20)
                
                # Latest closing prices
                close_non_sp = data["ohlcv"][-1][non_sp_ticker]['close']
                close_sp = data["ohlcv"][-1][sp_ticker]['close']
                
                # Check if there's an observable divergence in the latest price from the SMA
                # This simplistic approach invests in the one that is below its 20-day SMA
                # assuming it will revert back to the mean
                sma_diff_non_sp = (close_non_sp - sma_non_sp[-1]) / sma_non_sp[-1]
                sma_diff_sp = (close_sp - sma_sp[-1]) / sma_sp[-1]

                if sma_diff_non_sp < sma_diff_sp:
                    # Non S&P 500 company is comparatively lower, invest here
                    allocation[non_sp_ticker] = 0.5  # Example allocation, adjust based on strategy needs
                else:
                    # S&P 500 company is comparatively lower, invest here
                    allocation[sp_ticker] = 0.5  # Example allocation
                
            except Exception as e:
                log(f"Error processing pair {pair}: {str(e)}")
        
        if not allocation:
            # If no pairs were found suitable, don't invest
            return TargetAllocation({})
        
        return TargetAllocation(allocation)