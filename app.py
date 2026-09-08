import streamlit as st
import pandas as pd
import plotly.express as px
from model import evaluate
from storage import history, save_snapshot
from data_providers import load_latest_inputs
from backtest import summarize_crises

st.set_page_config(page_title="AI Exit-Trigger Dashboard v3",layout="wide")
st.title("AI / Macro Exit-Trigger Dashboard v3")
st.caption("Live monitoring + historical stress-test / backtest workspace.")

tab_live,tab_backtest,tab_rules=st.tabs(["Live dashboard","Backtest","Model rules"])

if "i" not in st.session_state:
    st.session_state.i=load_latest_inputs()
i=st.session_state.i

with tab_live:
    with st.sidebar:
        st.header("Inputs")
        i.azure_growth=st.number_input("Azure/cloud growth %",value=float(i.azure_growth))
        i.nvidia_dc_growth=st.number_input("Nvidia DC growth %",value=float(i.nvidia_dc_growth))
        i.datacenter_vacancy=st.number_input("Data-center vacancy %",value=float(i.datacenter_vacancy))
        i.hyperscaler_capex_cut_count=st.number_input("Hyperscalers cutting CapEx",0,6,int(i.hyperscaler_capex_cut_count))
        i.cape=st.number_input("Shiller CAPE",value=float(i.cape))
        i.top10_weight=st.number_input("S&P500 top-10 weight %",value=float(i.top10_weight))
        i.financing_stress_level=st.slider("Financing/FCF stress",0,4,int(i.financing_stress_level))
        i.us_unemployment=st.number_input("US unemployment %",value=float(i.us_unemployment))
        i.ai_layoff_stress=st.slider("AI layoff stress",0,4,int(i.ai_layoff_stress))
        i.saas_credit_stress=st.slider("SaaS/private-credit stress",0,4,int(i.saas_credit_stress))
        i.us_inflation=st.number_input("US inflation %",value=float(i.us_inflation))
        i.euro_macro_stress=st.slider("Euro macro stress",0,4,int(i.euro_macro_stress))
        i.brent=st.number_input("Brent USD/bbl",value=float(i.brent))
        i.geopolitical_stress=st.slider("Geopolitical stress",0,7,int(i.geopolitical_stress))

    r=evaluate(i)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Risk score",f"{r['total']}/100")
    c2.metric("Regime",r["regime"])
    c3.metric("Emergency",f"{r['emergency_count']}/5")
    action={"JAUDA":"Stay Jauda 16–55","WATCH":"Monitor","RISK REDUCTION":"Consider Izaugsme 55–62",
            "DEFENSIVE":"Consider defensive allocation"}[r["regime"]]
    c4.metric("Model action",action)
    st.progress(r["total"]/100)

    st.subheader("Risk blocks")
    rdf=pd.DataFrame({"Block":r["blocks"].keys(),"Score":r["blocks"].values()})
    st.plotly_chart(px.bar(rdf,x="Score",y="Block",orientation="h",text="Score"),use_container_width=True)

    st.subheader("Emergency triggers")
    for k,v in r["emergency"].items():
        st.write(("🔴 " if v else "🟢 ")+k)

    if st.button("Save snapshot",type="primary"):
        save_snapshot(r); st.success("Saved")

    st.subheader("History")
    h=history()
    if h.empty:
        st.info("No history yet.")
    else:
        fig=px.line(h,x="ts",y="total",markers=True)
        for y in [40,55,70]: fig.add_hline(y=y,line_dash="dot")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(h.sort_values("ts",ascending=False),use_container_width=True)

with tab_backtest:
    st.subheader("Historical stress-test")
    st.warning("Included crisis templates are a mechanics demo, not a point-in-time validated historical dataset.")
    summary,detail=summarize_crises()
    disp=summary.copy()
    for c in [x for x in disp.columns if x.endswith("_cagr") or x.endswith("_max_dd")]:
        disp[c]=(disp[c]*100).round(1).astype(str)+"%"
    st.dataframe(disp,use_container_width=True)

    crisis=st.selectbox("Select stress period",list(detail.keys()))
    bt=detail[crisis].copy()
    fig_score=px.line(bt,x="date",y="score",markers=True,title=f"{crisis}: model score")
    for y in [40,55,70]: fig_score.add_hline(y=y,line_dash="dot")
    st.plotly_chart(fig_score,use_container_width=True)

    wealth=bt[["date","stock_wealth","balanced_wealth","strategy_wealth"]].melt(
        id_vars="date",var_name="Portfolio",value_name="Wealth")
    st.plotly_chart(px.line(wealth,x="date",y="Wealth",color="Portfolio",
                            title=f"{crisis}: wealth comparison"),use_container_width=True)
    st.caption("JAUDA/WATCH = 100% equity; RISK REDUCTION = 50/50; DEFENSIVE = 100% bonds.")

with tab_rules:
    st.markdown("""
### Regimes
- **0–39:** JAUDA
- **40–54:** WATCH
- **55–69:** RISK REDUCTION
- **70–100:** DEFENSIVE
- **Emergency:** 3 of 5 critical triggers => DEFENSIVE

### Emergency 3/5 triggers
1. Cloud growth below 25%
2. Nvidia Data Center growth below 10%
3. Multiple hyperscalers cut CapEx
4. US unemployment above 5%
5. Data-center vacancy above 5%

### Backtest caveat
A robust historical test must avoid look-ahead bias, revised macro data, survivorship bias and using indicators that did not exist in earlier crises.
""")
