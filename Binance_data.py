# Import requests module to make HTTP requests
import requests
# Import pandas module to manipulate dataframes
import pandas as pd
# Import datetime module to convert dates
import datetime
# Import pytz module to handle time zones
import pytz
from urllib.parse import urljoin


# Define the base URL for Binance API
base_url = "https://api.binance.com"
# Define the endpoint for K-line data
endpoint = "/api/v3/klines"
# Define the start date and end date as datetime objects
# You can change them according to your needs
# Get the current date
current_date = datetime.datetime.now().date()

# Set the start date as today's date
start_date = datetime.datetime(2023, 3, 11)
# Set the end date as tomorrow's date
end_date = datetime.datetime(2023, 7, 25)
# Define the time zone you want to use
# You can change it according to your needs
time_zone = pytz.timezone("Asia/Kolkata")
# Define the interval you want to use
# You can change it according to your needs
interval = "5m"
number, unit = interval[:-1], interval[-1]
# Convert the number to an integer or a float
number = int(number) if number.isdigit() else float(number)
# Convert the unit to a valid timedelta keyword argument
unit = {"m": "minutes", "h": "hours", "s": "seconds"}[unit]
# Create a timedelta object using the number and the unit
interval = datetime.timedelta(**{unit: number})
# Define the limit you want to use
# The maximum value is 1000
limit = 1000
# Initialize an empty dataframe to store the data
btc_ohlcv = pd.DataFrame()
# Initialize a variable to store the current start time
current_start_time = start_date
# Loop until the current start time is equal or greater than the end date
while current_start_time < end_date:
    # Convert the current start time to milliseconds since the epoch and adjust for the time zone
    startTime = int(time_zone.localize(current_start_time).timestamp() * 1000)
    # Calculate the current end time by adding the interval times the limit and subtracting one millisecond
    current_end_time = current_start_time + datetime.timedelta(
        minutes=interval.total_seconds() / 60 * limit) - datetime.timedelta(milliseconds=1)

    current_end_time = min(current_end_time, end_date)
    # Convert the current end time to milliseconds since the epoch and adjust for the time zone
    endTime = int(time_zone.localize(current_end_time).timestamp() * 1000)
    # Define the parameters for the request
    params = {
        "symbol": "BTCTUSD",  # The trading pair
        "interval": '5m',  # The candlestick interval
        "limit": limit,  # The number of data points to return
        "startTime": startTime,  # The start time of the data
        "endTime": endTime  # The end time of the data
    }
    # Make the request and get the response
    response = requests.get(urljoin(base_url, endpoint), params=params)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response as JSON
        data = response.json()
        # Convert the data to a pandas dataframe
        df = pd.DataFrame(data, columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time",
                                         "Quote asset volume", "Number of trades", "Taker buy base asset volume",
                                         "Taker buy quote asset volume", "Ignore"])
        # Drop the unnecessary columns
        df = df.drop(["Close time", "Quote asset volume", "Number of trades", "Taker buy base asset volume",
                      "Taker buy quote asset volume", "Ignore"], axis=1)
        # Convert the open time column to datetime format and then to the time zone
        df["Open time"] = pd.to_datetime(df["Open time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(time_zone)
        # Set the open time column as the index
        df = df.set_index("Open time")
        # Append the dataframe to btc_ohlcv dataframe
        btc_ohlcv = pd.concat([btc_ohlcv, df]) if not btc_ohlcv.empty else df
    else:
        # Print the status code and the error message
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
    # Update the current start time by adding one millisecond to the current end time
    current_start_time = current_end_time + datetime.timedelta(milliseconds=1)

pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# Print some rows of btc_ohlcv dataframe
# print(btc_ohlcv['Close'])
# print(btc_ohlcv.tail())
