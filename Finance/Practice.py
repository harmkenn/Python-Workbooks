import pandas as pd
from alpha_vantage.timeseries import TimeSeries

# Replace with your Alpha Vantage API key
ts = TimeSeries(key='1QY7H4HWEB4WXWWJ', output_format='pandas')

# Try with a different symbol if ^FTSE doesn't work
try:
    data, meta_data = ts.get_intraday(symbol='^FTSE', interval='60min', outputsize='full')
    print(data.head())
except ValueError as e:
    print(f"Error fetching data: {e}")



# 1QY7H4HWEB4WXWWJ
