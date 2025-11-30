from sqlmodel import Session, select
from .models import Task

def create_task(engine, task: Task):
    with Session(engine) as s:
        s.add(task)
        s.commit()
        s.refresh(task)
        return task

def get_tasks(engine):
    with Session(engine) as s:
        tasks = s.exec(select(Task).order_by(Task.priority, Task.due_at)).all()
        return tasks

def update_task(engine, task_id, new_task: Task):
    with Session(engine) as s:
        task = s.get(Task, task_id)
        if not task:
            raise Exception("Not found")
        for k,v in new_task.dict(exclude_unset=True).items():
            setattr(task, k, v)
        s.add(task); s.commit(); s.refresh(task)
        return task

def delete_task(engine, task_id):
    with Session(engine) as s:
        task = s.get(Task, task_id)
        if not task:
            raise Exception("Not found")
        s.delete(task); s.commit()
        return {"ok": True}
