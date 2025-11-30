from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from .models import Task
from datetime import datetime, timezone

def check_and_send_reminders(engine):
    with Session(engine) as s:
        now = datetime.now(timezone.utc)
        q = s.exec(select(Task).where(Task.due_at != None, Task.remind_sent == False))
        tasks = q.all()
        for t in tasks:
            try:
                due = t.due_at
                # parse if stored as string
                if isinstance(due, str):
                    due_dt = datetime.fromisoformat(due)
                else:
                    due_dt = due
                # if due within next X minutes/hours, 'send' reminder
                delta = (due_dt - now).total_seconds()
                if 0 < delta <= 60*60:  # within next hour
                    # for demo: just mark remind_sent True; optionally call external API
                    t.remind_sent = True
                    s.add(t); s.commit()
                    print(f"Reminder: {t.title} due at {t.due_at}")
            except Exception as e:
                print("reminder error", e)

def start_scheduler(engine):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: check_and_send_reminders(engine), "interval", seconds=60)
    scheduler.start()
    return scheduler
