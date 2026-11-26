import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

COLUMNS = ["date", "series", "value", "source"]

#load .env from the project root (^^ two folder up)
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(ENV_PATH)

def get_fred_client() -> Fred:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError(f"FRED_API_KEY not found. Check {ENV_PATH}")
    return Fred(api_key=api_key)

def fetch_fred(series: str, start:str, fred: Fred | None = None) -> pd.DataFrame:
    fred = fred or get_fred_client()

    #returns a pandas Series: Index = dates, values = numbers
    s = fred.get_series(series, observation_start=start)

    if s.empty:
        return pd.DataFrame(columns=COLUMNS)

    s = s.dropna() #dropped NaN (holidays)

    df = s.reset_index()
    df.columns = ["date", "value"]
    df["series"] = series
    df["source"] = "FRED"

    df["date"] = pd.to_datetime(df["date"]).dt.date
    df['value'] = df["value"].astype(float)

    return df[COLUMNS]

if __name__ == "__main__":
    test = fetch_fred("T10Y2Y", "2024-01-01")
    print(test.head())
    print(test.dtypes)
    print(len(test), "rows") 