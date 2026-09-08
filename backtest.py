import pandas as pd
import numpy as np

REGIME_EQUITY={"JAUDA":1.0,"WATCH":1.0,"RISK REDUCTION":0.5,"DEFENSIVE":0.0}

def max_drawdown(series):
    s=pd.Series(series).astype(float)
    peak=s.cummax()
    return float((s/peak-1).min())

def cagr(series, periods_per_year=12):
    s=pd.Series(series).dropna().astype(float)
    if len(s)<2 or s.iloc[0]<=0: return np.nan
    years=(len(s)-1)/periods_per_year
    if years<=0: return np.nan
    return float((s.iloc[-1]/s.iloc[0])**(1/years)-1)

def run_regime_backtest(df, stock_col="stock_return", bond_col="bond_return", regime_col="regime"):
    x=df.copy().reset_index(drop=True)
    x["equity_weight"]=x[regime_col].map(REGIME_EQUITY).fillna(1.0)
    x["strategy_return"]=x["equity_weight"]*x[stock_col]+(1-x["equity_weight"])*x[bond_col]
    x["stock_wealth"]=(1+x[stock_col]).cumprod()
    x["balanced_wealth"]=(1+(0.5*x[stock_col]+0.5*x[bond_col])).cumprod()
    x["strategy_wealth"]=(1+x["strategy_return"]).cumprod()
    stats={
        "strategy_cagr":cagr(x["strategy_wealth"]),
        "strategy_max_dd":max_drawdown(x["strategy_wealth"]),
        "stock_cagr":cagr(x["stock_wealth"]),
        "stock_max_dd":max_drawdown(x["stock_wealth"]),
        "balanced_cagr":cagr(x["balanced_wealth"]),
        "balanced_max_dd":max_drawdown(x["balanced_wealth"]),
    }
    return x,stats

def sample_crisis_backtest():
    templates={
      "Dot-com 2000-02":[
        ("1999-07",35,0.02,0.005),("1999-10",42,0.04,0.004),("2000-01",48,-0.02,0.006),
        ("2000-04",58,-0.09,0.010),("2000-07",63,-0.04,0.008),("2000-10",72,-0.08,0.009),
        ("2001-01",76,-0.05,0.011),("2001-04",81,-0.06,0.012),("2001-07",84,-0.07,0.010),
        ("2001-10",88,-0.10,0.013),("2002-01",82,-0.03,0.009),("2002-04",77,-0.05,0.008),
        ("2002-07",74,-0.07,0.007),("2002-10",65,0.08,0.004)],
      "GFC 2007-09":[
        ("2007-01",38,0.02,0.005),("2007-04",44,0.03,0.004),("2007-07",51,-0.02,0.006),
        ("2007-10",57,-0.04,0.008),("2008-01",63,-0.06,0.010),("2008-04",68,-0.03,0.009),
        ("2008-07",74,-0.09,0.011),("2008-10",89,-0.17,0.015),("2009-01",86,-0.08,0.012),
        ("2009-04",71,0.10,0.004),("2009-07",59,0.08,0.003),("2009-10",46,0.05,0.002)],
      "Covid 2020":[
        ("2019-10",34,0.02,0.003),("2020-01",38,0.01,0.004),("2020-02",49,-0.08,0.006),
        ("2020-03",82,-0.13,0.010),("2020-04",69,0.12,-0.002),("2020-05",55,0.05,0.001),
        ("2020-06",43,0.02,0.001),("2020-07",36,0.06,0.000)],
      "2022 inflation bear":[
        ("2021-10",36,0.03,-0.005),("2022-01",45,-0.05,-0.020),("2022-04",56,-0.08,-0.030),
        ("2022-07",64,-0.04,-0.015),("2022-10",72,-0.07,0.010),("2023-01",61,0.06,0.015),
        ("2023-04",49,0.04,0.010),("2023-07",39,0.05,0.005)]
    }
    rows=[]
    for crisis,data in templates.items():
        for date,score,sr,br in data:
            reg="DEFENSIVE" if score>=70 else "RISK REDUCTION" if score>=55 else "WATCH" if score>=40 else "JAUDA"
            rows.append({"crisis":crisis,"date":pd.to_datetime(date),"score":score,"regime":reg,
                         "stock_return":sr,"bond_return":br})
    return pd.DataFrame(rows)

def summarize_crises():
    df=sample_crisis_backtest()
    out=[]; detail={}
    for crisis,g in df.groupby("crisis"):
        bt,stats=run_regime_backtest(g)
        out.append({
            "crisis":crisis,
            "first_watch":g.loc[g["score"]>=40,"date"].min(),
            "first_risk_reduction":g.loc[g["score"]>=55,"date"].min(),
            "first_defensive":g.loc[g["score"]>=70,"date"].min(),
            **stats
        })
        detail[crisis]=bt
    return pd.DataFrame(out),detail
