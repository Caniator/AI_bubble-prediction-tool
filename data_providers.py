import os, requests
from dotenv import load_dotenv
from model import Inputs
load_dotenv()

def fred_series(series_id, limit=24):
    key=os.getenv("FRED_API_KEY","")
    if not key:
        return []
    r=requests.get("https://api.stlouisfed.org/fred/series/observations",
        params={"series_id":series_id,"api_key":key,"file_type":"json","sort_order":"desc","limit":limit},
        timeout=20)
    r.raise_for_status()
    return r.json().get("observations",[])

def fred_latest(series_id):
    for o in fred_series(series_id,10):
        try:
            return float(o["value"])
        except Exception:
            pass
    return None

def fred_yoy(series_id):
    obs=list(reversed(fred_series(series_id,14)))
    vals=[]
    for o in obs:
        try: vals.append(float(o["value"]))
        except Exception: vals.append(None)
    vals=[v for v in vals if v is not None]
    if len(vals)<13:
        return None
    return (vals[-1]/vals[-13]-1)*100

def load_latest_inputs():
    i=Inputs()
    x=fred_latest("UNRATE")
    if x is not None: i.us_unemployment=x
    x=fred_yoy("CPIAUCSL")
    if x is not None: i.us_inflation=x
    x=fred_latest("DCOILBRENTEU")
    if x is not None: i.brent=x
    return i
