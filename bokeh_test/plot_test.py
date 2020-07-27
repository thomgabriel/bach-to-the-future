from tqdm import tqdm
import pandas as  pd
import ta
from datetime import datetime
import talib as tb
from time import sleep
from bokeh.io import output_notebook, show
from bokeh.plotting import figure
import dateparser
from backtest.util.api_ftx import FtxClient



ftx = FtxClient()
market_name = 'BTC-PERP'
resolution = 3600 # TimeFrame in seconds.
limit = 5000
start_time = datetime.fromisoformat('2020-05-01 00:00:00').timestamp()
end_time = datetime.now().timestamp()

ohlcv = pd.DataFrame(data=ftx.get_historical_data(market_name,resolution,limit,start_time,end_time))
ohlcv.columns = ["Close", "High", "Low", "Open","datetime", 'time', "Volume"]
ohlcv.datetime = ohlcv.datetime.apply(lambda x: dateparser.parse(x[:18]))

# //SMA'S
ma50 = ta.trend.SMAIndicator(ohlcv.Close,50).sma_indicator() 
ma20 = ta.trend.SMAIndicator(ohlcv.Close,20).sma_indicator() 
# //BOLLINGER BANDS
bb = ta.volatility.BollingerBands(ohlcv.Close,20)
bb_top = bb.bollinger_hband()
bb_bottom = bb.bollinger_lband()
# //MACD'S Fast EMA 
ema1= ta.trend.EMAIndicator(ohlcv.Close,12).ema_indicator()
ema2 = ta.trend.EMAIndicator(ema1,12).ema_indicator()
differenceFast = ema1 - ema2
zerolagEMA = ema1 + differenceFast
demaFast = (2 * ema1) - ema2
# //MACD'S Slow EMA 
emas1= ta.trend.EMAIndicator(ohlcv.Close,26).ema_indicator()
emas2 = ta.trend.EMAIndicator(emas1,26).ema_indicator()
differenceSlow = emas1 - emas2
zerolagslowMA = emas1 + differenceSlow
demaSlow = (2 * emas1) - emas2
# //MACD LINE
ZeroLagMACD = demaFast - demaSlow
# //SIGNAL LINE
emasig1 = ta.trend.EMAIndicator(ZeroLagMACD,9).ema_indicator()
emasig2 = ta.trend.EMAIndicator(emasig1,9).ema_indicator()
signal = (2 * emasig1) - emasig2
macdz_hist = ZeroLagMACD -signal
# //LINEAR REGRESSION
linreg = tb.LINEARREG(ma50,10)



from bokeh.io import output_notebook, show
from bokeh.plotting import figure
p = figure(plot_width=1800, plot_height=800)
p.line(ohlcv.datetime, ohlcv.Close, line_width=2, color = 'blue',legend_label="Close Price")
p.line(ohlcv.datetime, bb_top, line_width=2, color = 'orange', legend_label="BBands HBand")
p.line(ohlcv.datetime, bb_bottom, line_width=2, color = 'orange',legend_label="BBands LBand")
p.circle(x, x, legend_label="y=x", fill_color="white", size=8)

show(p)