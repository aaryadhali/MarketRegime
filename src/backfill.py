import time
from src.config import START_DATE, TICKERS, FRED_SERIES
from src.db import get_connection, insert_prices, insert_indicators
from src.sources.yahoo import fetch_prices
from src.sources.fred import fetch_fred, get_fred_client


def load_ticker(con, ticker:str) -> int:
    df = fetch_prices(ticker, START_DATE)
    added = insert_prices(con, df)
    #print(ticker, len(df), df['ticker'].unique() if not df.empty else "EMPTY")
    print(f"{ticker}: downloaded {len(df)}, added {added}")
    #return insert_prices(con, df)
    return added

def load_fred_series(con, series: str, fred) -> int:
    df = fetch_fred(series, START_DATE, fred)
    added = insert_indicators(con, df)
    print(f"{series}: downloaded {len(df)}, added {added}")
    return added


def print_market_summary(con) -> None:
    summary = con.execute("""
        SELECT ticker,
            COUNT(*) AS rows,
            MIN(date) AS first_date,
            MAX(date) AS last_date
        FROM market_data
        GROUP BY ticker
        ORDER BY ticker
    """).df()
    print("\n=====Market Data Table Summary=====")
    print(summary.to_string(index=False))

def print_indicator_summary(con) -> None:
    indicator_summary = con.execute("""
        SELECT series,
            COUNT(*) AS rows,
            MIN(date) AS first_date,
            MAX(date) AS last_date
        FROM fred_indicators
        GROUP BY series
        ORDER BY series
    """).df()
    print("\n=====Fred Indicators Table Summary=====")
    print(indicator_summary.to_string(index=False))

def main():
    con = get_connection()
    failed = []

    for ticker in TICKERS:
        try:
            load_ticker(con, ticker)
            #print(f"{ticker}: {n} rows")
        except Exception as e:
            print(f"{ticker}: {e}")
            failed.append(ticker)
        time.sleep(1)

    fred = get_fred_client()
    for series in FRED_SERIES:
        try:
            load_fred_series(con, series, fred)
        except Exception as e:
            print(f"{series}: {e}")
            failed.append(series)
        time.sleep(0.5)
   
    if failed:
        print("Failed", failed)
    print_market_summary(con)
    print_indicator_summary(con)
    con.close()

if __name__ == "__main__":
    main()
    