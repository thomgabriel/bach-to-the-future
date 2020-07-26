from client import FtxClient
from datetime import datetime
import pandas as pd


ftx = FtxClient()

# print(ftx.get_future('BTC-PERP'))

market_name = 'BTC-PERP'
resolution = 900 # TimeFrame in seconds.
limit = 5000
start_time = datetime.fromisoformat('2020-05-01 00:00:00').timestamp()
end_time = datetime.now().timestamp()

data = ftx.get_historical_data(market_name,resolution,limit,start_time,end_time)

ohlcv = pd.DataFrame(data=ftx.get_historical_data(market_name,resolution,limit,start_time,end_time))
ohlcv.columns = ["Close", "High", "Low", "Open","datetime", 'time', "Volume"]

print((ohlcv))

# for x in ftx.list_futures():
# #    if x['name'] == 'BTC-PERP':
# #        print (x)
#     print(x['name'])