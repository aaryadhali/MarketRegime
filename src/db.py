import duckdb
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / 'data' / 'market.duckdb'

SCHEMA = [

    """
        CREATE TABLE IF NOT EXISTS market_data (
            date DATE,
            ticker VARCHAR,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume BIGINT,
            PRIMARY KEY (date, ticker))
    """,

    """
        CREATE TABLE IF NOT EXISTS fred_indicators (
            date DATE,
            series VARCHAR,
            value DOUBLE,
            source VARCHAR
            PRIMARY KEY (date, series)
        )
    """,
]

def get_connection(db_path: Path = DB_PATH)->duckdb.DuckDBPyConnection:
    """connect to the duck db file, create the tables if they are msising, and return the connection"""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))

    for stmt in SCHEMA: #loop over the statements in SCHEMA
        con.execute(stmt)
    return con

def insert_prices(con: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> int:
    """insert rows into market_data, skipping (ticker, date) pairs already there. Returns rows added"""
    if df.empty:
        return 0
    
    before = con.execute("SELECT COUNT(*) FROM market_data").fetchone()[0]

    con.register("new_rows", df)
    try:
        con.execute("""
            INSERT OR REPLACE INTO market_data (ticker, date, open, high, low, close, volume)
            SELECT ticker, date, open, high, low, close, volume FROM new_rows
        """)
    finally:
        con.unregister("new_rows")
    after = con.execute("SELECT COUNT(*) FROM market_data").fetchone()[0]
    return after - before

def add_indicators(con: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> int:
    #insert rows into indicators
    if df.empty:
        return 0

    before = con.execute("SELECT COUNT(*) FROM fred_indicators").fetchone()[0]

    con.register("new_rows", df)
    try:
        con.execute("""
            INSERT OR REPLACE INTO fred_indicators (date, series, value, source)
            SELECT date, series, value, source FROM new_rows
        """)
    finally:
        con.unregister("new_rows")

    after = con.execute("SELECT COUNT(*) FROM fred_indicators").fetchone()[0]
    return after - before

if __name__ == "__main__":
    con = get_connection()
    print(con.sql("SHOW TABLES"))
    print(f"data base file:{DB_PATH} (exists: {DB_PATH.exists()})")
    con.close()
