# runner.py
from apscheduler.schedulers.blocking import BlockingScheduler
from scanner import scan_universe
from telegram_notify import send_signal
import time
import json
import os

# simple dedupe store (in production gunakan redis/db)
DEDUP_FILE = "sent_signals.json"

def load_sent():
    if not os.path.exists(DEDUP_FILE):
        return {}
    with open(DEDUP_FILE, "r") as f:
        return json.load(f)

def save_sent(d):
    with open(DEDUP_FILE, "w") as f:
        json.dump(d, f)

def job_scan_and_notify():
    print("[SCAN] Starting scan...")
    signals = scan_universe()
    if not signals:
        print("[SCAN] No signals.")
        return
    sent = load_sent()
    for s in signals:
        key = f"{s['symbol']}_{s['entry']}"
        if key in sent:
            print(f"[SCAN] Already sent {key}")
            continue
        resp = send_signal(s)
        print("[NOTIFY] Sent", s['symbol'], resp)
        sent[key] = {"time": time.time(), "payload": s}
        save_sent(sent)

if __name__ == "__main__":
    sched = BlockingScheduler()
    # contoh: run setiap 60 menit
    sched.add_job(job_scan_and_notify, 'interval', minutes=60)
    print("[RUNNER] Scheduler started.")
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        print("Stopped scheduler")
