"""Contains methods and classes to collect data from
Yahoo Finance API
"""

from __future__ import annotations  

import pandas as pd  # Import pandas for data processing
import yfinance as yf  # Import yfinance to fetch Yahoo Finance data


# Wrapper for yfinance
class YahooDownloader:
    """Provides methods for retrieving daily stock data from Yahoo Finance API

    Attributes
    ----------
        start_date : str
            Start date of the data
        end_date : str
            End date of the data
        ticker_list : list
            List of stock tickers

    Methods
    -------
    fetch_data()
        Fetches data from Yahoo API
    """

    def __init__(self, start_date: str, end_date: str, ticker_list: list):
        self.start_date = start_date  # Initialize start date
        self.end_date = end_date      # Initialize end date
        self.ticker_list = ticker_list  # Initialize ticker list

    def fetch_data(self, proxy=None, auto_adjust=False) -> pd.DataFrame:
        """Fetches data from Yahoo API
        Parameters
        ----------
        auto_adjust: bool, automatically adjust all OHLC? Default is False.

        Returns
        -------
        `pd.DataFrame`
            7 columns: date, open, high, low, close, volume, and ticker (tic)
        """
        # Download and save data to pandas DataFrame
        data_df = pd.DataFrame()  # Initialize empty DataFrame
        num_failures = 0  # Track number of failed downloads
        for tic in self.ticker_list:  # Iterate through each ticker
            temp_df = yf.download(
                tic,
                start=self.start_date,
                end=self.end_date,
                proxy=proxy,
                auto_adjust=auto_adjust,
            )  # Download data for a single ticker
            if temp_df.columns.nlevels != 1:  # If columns are multi-index
                temp_df.columns = temp_df.columns.droplevel(1)  # Flatten to single index
            temp_df["tic"] = tic  # Add ticker column
            if len(temp_df) > 0:  # If data is not empty
                # data_df = data_df.append(temp_df)
                data_df = pd.concat([data_df, temp_df], axis=0)  # Concatenate to main DataFrame
            else:
                num_failures += 1  # Increment failure count
        if num_failures == len(self.ticker_list):  # If all downloads failed
            raise ValueError("no data is fetched.")  # Raise exception
        
        # Reset index to use default numeric index
        data_df = data_df.reset_index()
        
        try:
            # Standardize column names
            data_df.rename(
                columns={
                    "Date": "date",
                    "Adj Close": "adjcp", # Adjusted Close Price: adjusted for dividends and splits
                    "Close": "close",
                    "High": "high",
                    "Low": "low",
                    "Volume": "volume",
                    "Open": "open",
                    "tic": "tic",
                },
                inplace=True,
            )

            if not auto_adjust:  # If auto_adjust is False
                data_df = self._adjust_prices(data_df)  # Manually adjust prices
        except NotImplementedError:
            print("the features are not supported currently")  # Catch unhandled exceptions
            
        # Add a new column for day of the week (Monday=0)
        data_df["day"] = data_df["date"].dt.dayofweek
        # Convert date to standard string format for easier filtering
        data_df["date"] = data_df.date.apply(lambda x: x.strftime("%Y-%m-%d"))
        # Drop missing data
        data_df = data_df.dropna()
        data_df = data_df.reset_index(drop=True)  # Reset index
        print("Shape of DataFrame: ", data_df.shape)  # Print data shape

        data_df = data_df.sort_values(by=["date", "tic"]).reset_index(drop=True)  # Sort by date and ticker

        return data_df  # Return processed data

    def _adjust_prices(self, data_df: pd.DataFrame) -> pd.DataFrame:
        """Adjust OHLC prices based on the adjusted close price."""
        # Calculate adjustment factor
        data_df["adj"] = data_df["adjcp"] / data_df["close"]  
        
        for col in ["open", "high", "low", "close"]:  # Adjust Open, High, Low, Close
            data_df[col] *= data_df["adj"]

        # Drop the temporary adjusted close and adjustment factor columns
        return data_df.drop(["adjcp", "adj"], axis=1)

    def select_equal_rows_stock(self, df):
        """Filter stocks to ensure they have the required amount of data rows."""
        df_check = df.tic.value_counts()  # Count data rows per ticker
        df_check = pd.DataFrame(df_check).reset_index()  # Convert to DataFrame
        df_check.columns = ["tic", "counts"]  # Rename columns
        mean_df = df_check.counts.mean()  # Calculate average row count
        equal_list = list(df.tic.value_counts() >= mean_df)  # Check which tickers meet the mean
        names = df.tic.value_counts().index  # Get ticker names
        select_stocks_list = list(names[equal_list])  # Select eligible tickers
        df = df[df.tic.isin(select_stocks_list)]  # Keep only data for these tickers
        return df  # Return filtered DataFrame



# 2025 Dow Jones 30 (DJIA)
DJIA = [
    # Category I: Core Tech - 5 tickers
    'MSFT', 'AAPL', 'NVDA', 'CRM', 'CSCO',
    
    # Category II: Info & Health - 5 tickers
    'IBM', 'UNH', 'AMGN', 'JNJ', 'MRK',
    
    # Category III: Finance & Indus - 5 tickers
    'JPM', 'GS', 'AXP', 'TRV', 'V',
    
    # Category IV: Industrials & Mat - 5 tickers
    'CAT', 'MMM', 'BA', 'HON', 'SHW',
    
    # Category V: Consumer Giants I - 5 tickers
    'MCD', 'WMT', 'PG', 'KO', 'HD',
    
    # Category VI: Consumer Giants II & Energy - 5 tickers
    'DIS', 'NKE', 'AMZN', 'CVX', 'VZ',
]

# 2025 SSE 50 (Shanghai Stock Exchange), taking 30 tickers (SH30)
SH30 = [
    '600028.SS',  # Sinopec - Energy
    '600030.SS',  # CITIC Securities - Finance/Broker
    '600031.SS',  # Sany Heavy Industry - Machinery
    '600048.SS',  # Poly Developments - Real Estate
    '600050.SS',  # China Unicom - TMT
    '600276.SS',  # Hengrui Medicine - Healthcare
    '600406.SS',  # Nari Technology - Power Equipment
    '600519.SS',  # Kweichow Moutai - Consumer (Baijiu)
    '600690.SS',  # Haier Smart Home - Consumer Appliances
    '600809.SS',  # Shanxi Fenjiu - Consumer (Baijiu)
    '600887.SS',  # Yili Industrial - Consumer (Dairy)
    '600900.SS',  # China Yangtze Power - Utilities
    '601012.SS',  # LONGi Green Energy - New Energy/Solar
    '601088.SS',  # China Shenhua - Energy/Coal
    '601166.SS',  # Industrial Bank - Finance/Banking
    '601211.SS',  # Guotai Junan - Finance/Broker
    '601225.SS',  # Shaanxi Coal - Energy/Coal
    '601288.SS',  # Agricultural Bank of China - Finance/Banking
    '601318.SS',  # Ping An Insurance - Finance/Insurance
    '601328.SS',  # Bank of Communications - Finance/Banking
    '601398.SS',  # ICBC - Finance/Banking
    '601601.SS',  # China Pacific Insurance - Finance/Insurance
    '601628.SS',  # China Life Insurance - Finance/Insurance
    '601668.SS',  # China State Construction - Construction
    '601857.SS',  # PetroChina - Energy
    '601888.SS',  # China Tourism Group Duty Free - Consumer/Retail
    '601919.SS',  # COSCO SHIPPING Holdings - Transportation/Shipping
    '601899.SS',  # Zijin Mining - Basic Materials
    '601985.SS',  # CNNP - Utilities/Nuclear
    '601988.SS',  # Bank of China - Finance/Banking
] 


FTSE30 = [
    'AAL.L',  # Anglo American - Mining
    'ABF.L',  # Associated British Foods - Food & Retail
    'ADM.L',  # Admiral Group - Insurance
    'AHT.L',  # Ashtead Group - Industrial Rental
    'ALW.L',  # Allwyn - Materials/Gaming
    'ANTO.L', # Antofagasta - Copper Mining
    'AUTO.L', # Auto Trader Group - Online Marketplace
    'AV.L',   # Aviva - Insurance
    'AZN.L',  # AstraZeneca - Pharmaceuticals
    'BA.L',   # BAE Systems - Defense/Aerospace
    'BAB.L',  # Babcock International - Engineering
    'BATS.L', # British American Tobacco - Tobacco
    'BEZ.L',  # Beazley - Insurance
    'BKG.L',  # Berkeley Group - Real Estate
    'BNZL.L', # Bunzl - Distribution
    'BRBY.L', # Burberry - Luxury
    'BTRW.L', # Britvic/Breedon - Beverages/Construction
    'CCH.L',  # Coca-Cola HBC - Bottling
    'CNA.L',  # Centrica - Energy/Utilities
    'CPG.L',  # Compass Group - Catering
    'DCC.L',  # DCC plc - Energy/Tech
    'DPLM.L', # Diploma - Distribution
    'ENT.L',  # Entain - Gaming/Betting
    'EXPN.L', # Experian - Data/Credit
    'EZJ.L',  # easyJet - Airline
    'FCIT.L', # F&C Investment Trust - Investment
    'FRES.L', # Fresnillo - Precious Metals
    'GAW.L',  # Games Workshop - Entertainment
    'GSK.L',  # GSK - Pharmaceuticals
    'HIK.L',  # Hikma Pharmaceuticals - Healthcare
]

Nifty30= [
    # Conglomerates/Energy/Mining
    'RELIANCE.NS',  # Reliance Industries
    'ADANIENT.NS',  # Adani Enterprises
    'ONGC.NS',      # Oil & Natural Gas Corp
    'COALINDIA.NS', # Coal India

    # Core Finance/Banking
    'HDFCBANK.NS',  # HDFC Bank
    'ICICIBANK.NS', # ICICI Bank
    'SBIN.NS',      # State Bank of India
    'BAJFINANCE.NS',# Bajaj Finance
    'KOTAKBANK.NS', # Kotak Mahindra Bank
    'AXISBANK.NS',  # Axis Bank
    'BAJAJFINSV.NS',# Bajaj Finserv
    'SHRIRAMFIN.NS',# Shriram Finance

    # Technology/IT Services
    'TCS.NS',       # Tata Consultancy Services
    'INFY.NS',      # Infosys
    'HCLTECH.NS',   # HCL Technologies
    'TECHM.NS',     # Tech Mahindra

    # Industrials/Infrastructure/Utilities
    'LT.NS',        # Larsen & Toubro
    'NTPC.NS',      # NTPC
    'POWERGRID.NS', # Power Grid Corp
    'BEL.NS',       # Bharat Electronics

    # Consumer/FMCG
    'HINDUNILVR.NS',# Hindustan Unilever
    'ITC.NS',       # ITC Ltd
    'TATACONSUM.NS',# Tata Consumer Products

    # Auto/Consumer Durables
    'MARUTI.NS',    # Maruti Suzuki
    'M&M.NS',       # Mahindra & Mahindra
    'TITAN.NS',     # Titan Company

    # Pharma/Healthcare
    'SUNPHARMA.NS', # Sun Pharma
    'APOLLOHOSP.NS',# Apollo Hospitals

    # Basic Materials
    'ULTRACEMCO.NS',# UltraTech Cement
    'HINDALCO.NS'   # Hindalco Industries
]

# Configure settings
tickers = FTSE30 
indicat_pre = 'FTSE30_2016' 

START_DATE = "2016-01-01"
END_DATE = "2025-11-01"

# Initialize Downloader and fetch data
df_raw = YahooDownloader(start_date = START_DATE,
                                end_date = END_DATE,
                                ticker_list = tickers).fetch_data(proxy="http://127.0.0.1:7897")

print("Unique tickers before preprocessing:", df_raw['tic'].nunique())
print("Total rows before preprocessing:", len(df_raw))
print('Data distribution per ticker before preprocessing:', df_raw.groupby("tic").size())

import pandas as pd

# 1. Calculate row count for each ticker
tic_counts = df_raw.groupby("tic").size()

# 2. Find the maximum row count (complete time coverage)
N_max = tic_counts.max()

# 3. Filter tickers with fewer rows than N_max
missing_tics = tic_counts[tic_counts < N_max]
complete_tics = tic_counts[tic_counts == N_max]

print("\n--- Validation Results ---")
if missing_tics.empty:
    print("All tickers cover the full time range (Rows: {}).".format(N_max))
else:
    print("The following tickers have fewer rows than the full range ({}):".format(N_max))
    print(missing_tics)
    print("\n**These tickers may need to be filtered out.**")


print('\nComplete Tickers:', complete_tics.size, complete_tics.index.tolist())
print('\nIncomplete Tickers:', missing_tics.size, missing_tics.index.tolist())

print(df_raw.head())
print("\nRaw data shape:", df_raw.shape)
print("Raw data columns:", df_raw.columns)
print('Download Complete! ✅')

# 2. Add technical indicators using FeatureEngineer (Stockstats wrapper)
from finrl.meta.preprocessor.preprocessors import FeatureEngineer
import itertools

# stockstats technical indicator column names
INDICATORS = [
    "macd",
    "boll_ub",
    "boll_lb",
    "rsi_30",
    "cci_30",
    "dx_30",
    "close_30_sma",
    "close_60_sma",
]

# Note: Proxy might be needed for network-restricted environments
fe = FeatureEngineer(use_technical_indicator=True,
                     tech_indicator_list = INDICATORS,
                     use_vix=True,
                     use_turbulence=True,
                     user_defined_feature = False)

processed = fe.preprocess_data(df_raw)


# 3. Data Alignment: Complete missing date-ticker combinations
list_ticker = processed["tic"].unique().tolist()  # Unique tickers
list_date = list(pd.date_range(processed['date'].min(), processed['date'].max()).astype(str))  # Complete date range
combination = list(itertools.product(list_date, list_ticker))  # Cartesian product of dates and tickers

# Left merge with all combinations to fill gaps
processed_full = pd.DataFrame(combination, columns=["date", "tic"]).merge(processed, on=["date", "tic"], how="left")  
# Only keep dates that existed in the original dataset
processed_full = processed_full[processed_full['date'].isin(processed['date'])]  
processed_full = processed_full.sort_values(['date', 'tic'])  

# Fill missing values with 0
processed_full = processed_full.fillna(0)  

print(processed_full.head())  # Print sample data

print("Tickers in processed data:", processed['tic'].nunique())
print("Rows before completion:", len(processed))
print("Rows after completion:", len(processed_full))
print(processed_full.groupby("tic").size())


"""
Final data format example:
date        tic     close  volume
2020-01-01  AAPL    300    1000
2020-01-01  MSFT    150    2000
...
"""

# 4. Data Splitting functions

def data_split(df, start, end, target_date_col="date"):
    """
    Splits the dataset into training or testing sets based on date.
    :param df: (df) pandas dataframe
    :param start: (str) start date
    :param end: (str) end date
    :return: (df) pandas dataframe
    """
    data = df[(df[target_date_col] >= start) & (df[target_date_col] < end)]
    data = data.sort_values([target_date_col, "tic"], ignore_index=True)
    data.index = data[target_date_col].factorize()[0]
    return data


def data_split_with_window(df, start, end, window_size=0, target_date_col="date"):
    """
    Splits the dataset by date and includes a look-back window of data before the start date.
    :param df: pandas DataFrame
    :param start: Start date string
    :param end: End date string
    :param window_size: Number of previous dates to include
    :param target_date_col: Date column name
    :return: pandas DataFrame
    """
    # Main interval split
    data = df[(df[target_date_col] >= start) & (df[target_date_col] < end)]
    
    # If a window is required, get the preceding window_size dates
    if window_size > 0:
        prev_dates = df[df[target_date_col] < start][target_date_col].drop_duplicates().sort_values().tail(window_size)
        prev_data = df[df[target_date_col].isin(prev_dates)]
        data = pd.concat([prev_data, data], ignore_index=True)
    
    # Sort and re-index
    data = data.sort_values([target_date_col, "tic"], ignore_index=True)
    data.index = data[target_date_col].factorize()[0]
    
    return data


import shutil, os

# Create data directory, clear it if it already exists
data_folder = './data_test'
if os.path.exists(data_folder):
    shutil.rmtree(data_folder)  # Delete directory and contents
os.makedirs(data_folder, exist_ok=True)  # Create fresh directory


processed_full.to_csv(f'{data_folder}/{indicat_pre}.csv')

# Load CSV and verify
import pandas as pd
get_data = pd.read_csv(f'{data_folder}/{indicat_pre}.csv')
get_data = get_data.set_index(get_data.columns[0])
get_data.index.names = ['']
print(get_data.head())


