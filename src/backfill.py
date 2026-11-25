import time
from src.config import START_DATE, TICKERS
from src.db import get_connection, insert_prices
from src.sources.yahoo import fetch_prices

#START = "2005-01-01"

def load_ticker(con, ticker:str) -> int:
    df = fetch_prices(ticker, START_DATE)
    added = insert_prices(con, df)
    #print(ticker, len(df), df['ticker'].unique() if not df.empty else "EMPTY")
    print(f"{ticker}: downloaded {len(df)}, added {added}")
    #return insert_prices(con, df)
    return added


def print_summary(con) -> None:
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
   
    if failed:
        print("Failed", failed)
    print_summary(con)
    con.close()

if __name__ == "__main__":
    main()
    