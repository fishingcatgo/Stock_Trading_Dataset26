# 1. Introduction

This dataset is constructed for reinforcement learning-based multi-asset stock trading experiments in international financial markets. It contains daily market observations from four representative stock markets between 2016 and 2026.

The dataset includes:

* Daily adjusted open, high, low, and close prices
* Daily trading volume
* Calendar information
* Common technical indicators
* Market volatility information
* Financial turbulence measurements

The four market datasets are designed to support model training, validation, testing, cross-market comparison, and robustness evaluation for stock trading and portfolio allocation tasks.


# 2. Dataset Overview

The dataset covers four international stock markets, with 30 representative stocks selected from each market.

| Dataset | Market | Description | Number of Stocks | Date Range |
|---|---|---|---:|---|
| `DJIA_2025.csv` | United States | Stocks from the Dow Jones Industrial Average | 30 | 2016–2026 |
| `FTSE30_2025.csv` | United Kingdom | 30 representative stocks selected from the FTSE 100 | 30 | 2016–2026 |
| `Nifty30_2025.csv` | India | 30 representative stocks selected from the NIFTY 50 | 30 | 2016–2026 |
| `SH30_2025.csv` | China | 30 representative stocks selected from the SSE 50 | 30 | 2016–2026 |

The original daily stock data are collected from Yahoo Finance through the `yfinance` package. The raw data are subsequently adjusted, cleaned, aligned, and enriched with technical and risk-related indicators.


# 3. Dataset Directory Structure

The dataset directory is organized as follows:

```text
.
├── DJIA_2025.csv       # Daily data for 30 DJIA stocks
├── FTSE30_2025.csv     # Daily data for 30 representative FTSE stocks
├── Nifty30_2025.csv    # Daily data for 30 representative NIFTY stocks
├── SH30_2025.csv       # Daily data for 30 representative SSE stocks
├── Get_dataset.py      # Data downloading, preprocessing, and feature engineering script
└── README.md           # Dataset documentation
```


# 4. Data Format

Each row represents the daily market information of one stock on one trading date. The records are sorted first by date and then by ticker symbol.

| Column | Description |
|---|---|
| `date` | Trading date in `YYYY-MM-DD` format |
| `tic` | Stock ticker symbol used by Yahoo Finance |
| `close` | Adjusted daily closing price |
| `high` | Adjusted highest price of the trading day |
| `low` | Adjusted lowest price of the trading day |
| `open` | Adjusted opening price of the trading day |
| `volume` | Daily trading volume |
| `day` | Day of the week, where Monday is 0 and Friday is 4 |
| `macd` | Moving Average Convergence Divergence |
| `boll_ub` | Upper Bollinger Band |
| `boll_lb` | Lower Bollinger Band |
| `rsi_30` | 30-period Relative Strength Index |
| `cci_30` | 30-period Commodity Channel Index |
| `dx_30` | 30-period Directional Movement Index |
| `close_30_sma` | 30-period simple moving average of the closing price |
| `close_60_sma` | 60-period simple moving average of the closing price |
| `vix` | CBOE Volatility Index used as a market-level risk indicator |
| `turbulence` | Financial turbulence index calculated from historical market information |

The first unnamed column in each CSV file is the DataFrame index generated during export. It is not used as a market feature and can be removed when loading the data.

Example:

```python
import pandas as pd

data = pd.read_csv("dataset/DJIA_2025.csv", index_col=0)
print(data.head())
```


# 5. Data Generation and Preprocessing

The `Get_dataset.py` script performs the following steps:

* Downloads daily stock data from Yahoo Finance
* Adjusts the OHLC prices using the adjusted closing price
* Removes invalid and missing raw observations
* Adds the day-of-week feature
* Calculates technical indicators using FinRL
* Adds the VIX and financial turbulence indicators
* Completes missing date–ticker combinations
* Fills missing aligned values with zero
* Sorts the final data by date and ticker
* Exports the processed data as CSV files

The technical indicators used in the dataset are:

```python
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
```


# 6. How to Generate the Dataset

Step 1: Install the required environment.

```bash
pip install pandas yfinance finrl stockstats
```

Step 2: Select the target market and configure the date range in `Get_dataset.py`.

```python
# Select one market

tickers = DJIA
indicat_pre = "DJIA_2025"

START_DATE = "2016-01-01"
END_DATE = "2026-01-01"
```

The available market ticker lists are:

```python
DJIA
FTSE30
Nifty30
SH30
```

Step 3: Run the data generation script.

```bash
python Get_dataset.py
```

Step 4: Repeat the process for the remaining markets by changing `tickers` and `indicat_pre`.

Example:

```python
tickers = FTSE30
indicat_pre = "FTSE30_2025"
```


# 7. Data Usage

The generated datasets can be used for:

* Reinforcement learning-based stock trading
* Multi-asset portfolio allocation
* Market state representation learning
* Cross-market trading evaluation
* Risk-aware decision optimization
* Technical indicator-based financial forecasting
* Model robustness and generalization analysis

For reinforcement learning experiments, the dataset can be divided chronologically into training, validation, and testing periods to prevent future information leakage.


# 8. Notes

* The four markets have different trading calendars and public holidays; therefore, their exact numbers of trading days may differ.
* Technical indicators requiring historical windows may contain initialization values at the beginning of the dataset.
* The VIX is a U.S. market volatility indicator and is used as a common global risk proxy across the datasets.
* Missing date–ticker combinations introduced during data alignment are filled with zero by the preprocessing script.
* The CSV index column should be removed or ignored before model training.
* The datasets are intended for academic research and experimental evaluation only and should not be regarded as financial advice.
