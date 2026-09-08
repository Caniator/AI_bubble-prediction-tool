import sqlite3, json, os
from datetime import datetime, timezone
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
DB = os.getenv("DB_PATH","risk_history.db")

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS snapshots(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            total INTEGER NOT NULL,
            regime TEXT NOT NULL,
            emergency_count INTEGER NOT NULL,
            payload TEXT NOT NULL
        )""")
        con.commit()

def save_snapshot(result):
    init_db()
    with sqlite3.connect(DB) as con:
        con.execute("INSERT INTO snapshots(ts,total,regime,emergency_count,payload) VALUES(?,?,?,?,?)",
                    (datetime.now(timezone.utc).isoformat(),result["total"],result["regime"],
                     result["emergency_count"],json.dumps(result)))
        con.commit()

def history(limit=730):
    init_db()
    with sqlite3.connect(DB) as con:
        df = pd.read_sql_query(
            "SELECT ts,total,regime,emergency_count FROM snapshots ORDER BY ts DESC LIMIT ?",
            con, params=(limit,))
    if not df.empty:
        df["ts"]=pd.to_datetime(df["ts"],utc=True)
        df=df.sort_values("ts")
    return df

def latest_two():
    init_db()
    with sqlite3.connect(DB) as con:
        return con.execute("SELECT total,regime FROM snapshots ORDER BY ts DESC LIMIT 2").fetchall()
