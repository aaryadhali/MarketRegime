"""Dowbload daily prices from yahoo finance and reshape them to match prices table."""

import pandas as pd
import yfinance as yf

COLUMNS = ["ticker","date", "open", "high", "low", "close", "volume"]

def fetch_prices(ticker:str, start:str) -> pd.DataFrame:
    df = yf.download(ticker, start=start, auto_adjust=False, progress=False)

    if df.empty:
        return pd.DataFrame(columns=COLUMNS)

    #Newer yfinance vers return ("close", "SPY")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    df.columns = [c.lower() for c in df.columns]

    df['ticker'] = ticker

    #df['date'] = pd.to_datetime(df["date"]).dt.date #plain date no time zone
    df["volume"] = df["volume"].fillna(0).astype("int64")

    return df[COLUMNS]


if __name__ == "__main__":
    test = fetch_prices("SPY", "2024-01-01")
    print(test.head())
    print(test.dtypes)
    print(len(test), "rows")


    