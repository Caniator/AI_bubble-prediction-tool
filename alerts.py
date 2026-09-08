import os, smtplib, requests
from email.message import EmailMessage
from dotenv import load_dotenv
from storage import latest_two
load_dotenv()

def telegram(text):
    token=os.getenv("TELEGRAM_BOT_TOKEN","")
    chat=os.getenv("TELEGRAM_CHAT_ID","")
    if not token or not chat: return False
    r=requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                    json={"chat_id":chat,"text":text},timeout=20)
    r.raise_for_status()
    return True

def email_alert(subject, body):
    host=os.getenv("SMTP_HOST","")
    user=os.getenv("SMTP_USER","")
    pwd=os.getenv("SMTP_PASSWORD","")
    frm=os.getenv("ALERT_EMAIL_FROM","")
    to=os.getenv("ALERT_EMAIL_TO","")
    if not all([host,user,pwd,frm,to]): return False
    msg=EmailMessage()
    msg["Subject"]=subject
    msg["From"]=frm
    msg["To"]=to
    msg.set_content(body)
    with smtplib.SMTP(host,int(os.getenv("SMTP_PORT","587")),timeout=20) as s:
        s.starttls()
        s.login(user,pwd)
        s.send_message(msg)
    return True

def send_if_needed(result):
    rows=latest_two()
    prev_total=rows[1][0] if len(rows)>=2 else None
    prev_regime=rows[1][1] if len(rows)>=2 else None
    reasons=[]
    if prev_total is not None:
        for t in (40,55,70):
            if prev_total < t <= result["total"]:
                reasons.append(f"Score crossed {t}")
        if result["total"]-prev_total >= 10:
            reasons.append("Score jumped by >=10")
    if prev_regime and prev_regime != result["regime"]:
        reasons.append(f"Regime changed {prev_regime} -> {result['regime']}")
    if result["emergency_count"]>=3:
        reasons.append("Emergency 3/5 trigger active")
    if not reasons:
        return {"sent":False,"reasons":[]}
    body=(f"AI Exit-Trigger Alert\n\nScore: {result['total']}/100\n"
          f"Regime: {result['regime']}\nEmergency: {result['emergency_count']}/5\n\n"
          "Reasons:\n- " + "\n- ".join(reasons))
    sent=[]
    try:
        if telegram(body): sent.append("telegram")
    except Exception as e:
        sent.append("telegram_error:"+str(e))
    try:
        if email_alert("AI Exit-Trigger Alert",body): sent.append("email")
    except Exception as e:
        sent.append("email_error:"+str(e))
    return {"sent":bool(sent),"channels":sent,"reasons":reasons}
