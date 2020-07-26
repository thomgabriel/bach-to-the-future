import tools
import csv
from tqdm import tqdm
import logger
import statistics as st
import pandas as  pd
import numpy as np
import ta
import ccxt
from datetime import datetime
import talib as tb
from time import sleep


from bokeh.io import output_notebook, show
from bokeh.plotting import figure


symbol= 'BTC-PERP'
timeframe= '15m'
since= '2020-07-10T00:00:00Z'

exchange = ccxt.ftx()
ohlcv = pd.DataFrame(data=exchange.fetch_ohlcv(symbol, timeframe,exchange.parse8601 (since)))
ohlcv.columns = ["datetime", "Open", "High", "Low", "Close", "Volume"]
ohlcv.datetime = ohlcv.datetime.apply(lambda x: datetime.fromtimestamp(x / 1000))

# dates = np.array(ohlcv.datetime, dtype=np.datetime64)
print(ohlcv.datetime)

p = figure(plot_width=1800, plot_height=800, x_range=ohlcv.datetime)
p.line(ohlcv.Close, line_width=2)


show(p) # show the results