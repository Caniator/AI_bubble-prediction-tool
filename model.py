from dataclasses import dataclass, asdict

@dataclass
class Inputs:
    azure_growth: float = 43.0
    nvidia_dc_growth: float = 117.0
    datacenter_vacancy: float = 1.4
    hyperscaler_capex_cut_count: int = 0
    cape: float = 41.0
    top10_weight: float = 37.8
    financing_stress_level: int = 3
    us_unemployment: float = 4.1
    ai_layoff_stress: int = 2
    saas_credit_stress: int = 2
    us_inflation: float = 3.4
    euro_macro_stress: int = 3
    brent: float = 85.0
    geopolitical_stress: int = 4

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def evaluate(i: Inputs):
    azure = 0 if i.azure_growth > 35 else 3 if i.azure_growth >= 25 else 6 if i.azure_growth >= 15 else 10
    nvda = 0 if i.nvidia_dc_growth > 40 else 3 if i.nvidia_dc_growth >= 20 else 6 if i.nvidia_dc_growth >= 0 else 10
    dc = 0 if i.datacenter_vacancy < 3 else 3 if i.datacenter_vacancy < 5 else 6 if i.datacenter_vacancy < 8 else 10
    capex = 0 if i.hyperscaler_capex_cut_count == 0 else 3 if i.hyperscaler_capex_cut_count == 1 else 5

    financing = round(clamp(i.financing_stress_level,0,4)/4*8)
    valuation = 0 if i.cape < 25 else 2 if i.cape < 30 else 4 if i.cape < 35 else 6 if i.cape < 40 else 7
    concentration = 0 if i.top10_weight < 25 else 2 if i.top10_weight < 30 else 4 if i.top10_weight < 35 else 5

    unemployment = 0 if i.us_unemployment < 4.5 else 3 if i.us_unemployment < 4.8 else 6 if i.us_unemployment <= 5.2 else 10
    layoffs = round(clamp(i.ai_layoff_stress,0,4)/4*6)
    saas = round(clamp(i.saas_credit_stress,0,4)/4*5)
    inflation = 0 if i.us_inflation < 2.3 else 2 if i.us_inflation < 2.8 else 3 if i.us_inflation < 3.3 else 4 if i.us_inflation < 4 else 5
    europe = round(clamp(i.euro_macro_stress,0,4))

    energy = 0 if i.brent < 75 else 3 if i.brent < 90 else 6 if i.brent <= 110 else 8
    geo = round(clamp(i.geopolitical_stress,0,7))

    blocks = {
        "AI cycle break": azure + nvda + dc + capex,
        "Valuation & financing": financing + valuation + concentration,
        "Labor & macro": unemployment + layoffs + saas + inflation + europe,
        "Energy & geopolitics": energy + geo,
    }

    emergency = {
        "Cloud growth <25%": i.azure_growth < 25,
        "Nvidia DC growth <10%": i.nvidia_dc_growth < 10,
        "Multiple hyperscalers cut CapEx": i.hyperscaler_capex_cut_count >= 2,
        "US unemployment >5%": i.us_unemployment > 5,
        "Data-center vacancy >5%": i.datacenter_vacancy > 5,
    }

    total = sum(blocks.values())
    ecount = sum(emergency.values())

    if ecount >= 3 or total >= 70:
        regime = "DEFENSIVE"
    elif total >= 55:
        regime = "RISK REDUCTION"
    elif total >= 40:
        regime = "WATCH"
    else:
        regime = "JAUDA"

    return {"inputs":asdict(i),"blocks":blocks,"total":total,"emergency":emergency,
            "emergency_count":ecount,"regime":regime}
