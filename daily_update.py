from data_providers import load_latest_inputs
from model import evaluate
from storage import save_snapshot
from alerts import send_if_needed

def main():
    i=load_latest_inputs()
    r=evaluate(i)
    save_snapshot(r)
    a=send_if_needed(r)
    print("Score:",r["total"])
    print("Regime:",r["regime"])
    print("Emergency:",r["emergency_count"])
    print("Alert:",a)

if __name__=="__main__":
    main()
