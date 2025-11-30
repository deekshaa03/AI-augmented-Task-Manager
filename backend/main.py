# from fastapi import FastAPI, HTTPException, Body
# from fastapi.middleware.cors import CORSMiddleware
# from sqlmodel import SQLModel, create_engine, Session, select, Field
# from typing import Optional, List
# import os, httpx, re, logging
# from dotenv import load_dotenv
# from datetime import datetime
# from pydantic import BaseModel

# load_dotenv()

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # -------------------- Models --------------------
# class Task(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     title: str
#     description: str
#     reminder_time: Optional[str] = None
#     priority: int = Field(default=3, ge=1, le=5)
#     completed: bool = False
#     set_reminder: bool = False

# class TaskRead(BaseModel):
#     id: int
#     title: str
#     description: str
#     reminder_time: Optional[str]
#     priority: int
#     completed: bool
#     set_reminder: bool

# # -------------------- Database --------------------
# DATABASE_URL = "sqlite:///tasks.db"
# engine = create_engine(DATABASE_URL, echo=False)
# SQLModel.metadata.create_all(engine)

# # -------------------- FastAPI App --------------------
# app = FastAPI(title="AI Task Manager Backend")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # -------------------- CRUD --------------------
# def create_task(task: Task) -> Task:
#     with Session(engine) as session:
#         session.add(task)
#         session.commit()
#         session.refresh(task)
#         return task

# def get_tasks() -> List[Task]:
#     with Session(engine) as session:
#         tasks = session.exec(select(Task)).all()
#         return tasks

# def update_task(task_id: int, updates: dict) -> Task:
#     with Session(engine) as session:
#         task = session.get(Task, task_id)
#         if not task:
#             raise HTTPException(status_code=404, detail="Task not found")
#         for key, value in updates.items():
#             if hasattr(task, key):
#                 setattr(task, key, value)
#         session.commit()
#         session.refresh(task)
#         return task

# def delete_task(task_id: int):
#     with Session(engine) as session:
#         task = session.get(Task, task_id)
#         if not task:
#             raise HTTPException(status_code=404, detail="Task not found")
#         session.delete(task)
#         session.commit()

# def bulk_update_tasks(task_ids: List[int], updates: dict):
#     with Session(engine) as session:
#         for task_id in task_ids:
#             task = session.get(Task, task_id)
#             if task:
#                 for key, value in updates.items():
#                     if hasattr(task, key):
#                         setattr(task, key, value)
#         session.commit()

# # -------------------- API --------------------
# @app.post("/tasks", response_model=TaskRead)
# def add_task(task: Task):
#     try:
#         return create_task(task)
#     except Exception as e:
#         logger.error(f"Error adding task: {e}")
#         raise HTTPException(status_code=500, detail="Failed to add task")

# @app.get("/tasks", response_model=List[TaskRead])
# def list_tasks():
#     try:
#         return get_tasks()
#     except Exception as e:
#         logger.error(f"Error listing tasks: {e}")
#         raise HTTPException(status_code=500, detail="Failed to list tasks")

# @app.put("/tasks/{task_id}", response_model=TaskRead)
# def update_task_endpoint(task_id: int, updates: dict = Body(...)):
#     try:
#         return update_task(task_id, updates)
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error updating task {task_id}: {e}")
#         raise HTTPException(status_code=500, detail="Failed to update task")

# @app.delete("/tasks/{task_id}")
# def delete_task_endpoint(task_id: int):
#     try:
#         delete_task(task_id)
#         return {"message": "Task deleted successfully"}
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error deleting task {task_id}: {e}")
#         raise HTTPException(status_code=500, detail="Failed to delete task")

# @app.put("/tasks/bulk")
# def bulk_update_endpoint(task_ids: List[int] = Body(...), updates: dict = Body(...)):
#     try:
#         bulk_update_tasks(task_ids, updates)
#         return {"message": "Bulk update successful"}
#     except Exception as e:
#         logger.error(f"Error in bulk update: {e}")
#         raise HTTPException(status_code=500, detail="Failed to bulk update tasks")

# # -------------------- AI Suggestions --------------------
# async def groq_generate_plain(prompt: str) -> dict:
#     api_key = os.getenv("GROQ_API_KEY")
#     if not api_key:
#         raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")
#     url = "https://api.groq.com/openai/v1/chat/completions"
#     headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
#     enhanced_prompt = f"Based on this work: '{prompt}', suggest 3-5 actionable tasks as Title: Description (Priority X)."
#     payload = {
#         "model": "llama-3.1-8b-instant",
#         "messages": [
#             {"role": "system", "content": "You are an AI task assistant."},
#             {"role": "user", "content": enhanced_prompt}
#         ],
#         "max_tokens": 300,
#         "temperature": 0.7
#     }
#     async with httpx.AsyncClient() as client:
#         resp = await client.post(url, headers=headers, json=payload)
#     if resp.status_code != 200:
#         raise HTTPException(status_code=500, detail=f"Groq API Error: {resp.text}")
#     data = resp.json()
#     content = re.sub(r'\[.*\]', '', data["choices"][0]["message"]["content"], flags=re.DOTALL).strip()
#     lines = [line.strip() for line in content.splitlines() if line.strip()]
#     tasks = []
#     for line in lines:
#         if ':' in line:
#             title, rest = line.split(':', 1)
#             priority_match = re.search(r'\(Priority (\d)\)', rest)
#             priority = int(priority_match.group(1)) if priority_match else 3
#             description = re.sub(r'\(Priority \d\)', '', rest).strip()
#             tasks.append({"title": title.strip(), "description": description, "priority": priority})
#         else:
#             tasks.append({"title": "Suggestion", "description": line, "priority": 3})
#     return {"suggestions": tasks}

# @app.post("/suggest")
# async def suggest_plain(body: dict = Body(...)):
#     text = body.get("text", "").strip()
#     if not text:
#         raise HTTPException(status_code=400, detail="Missing or empty 'text'")
#     return await groq_generate_plain(text)


from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine, Session, select, Field
from typing import Optional, List
import os, httpx, re, logging
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------- Models --------------------
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    reminder_time: Optional[str] = None
    priority: int = Field(default=3, ge=1, le=5)
    completed: bool = False
    set_reminder: bool = False

class TaskRead(BaseModel):
    id: int
    title: str
    description: str
    reminder_time: Optional[str]
    priority: int
    completed: bool
    set_reminder: bool

# -------------------- Database --------------------
DATABASE_URL = "sqlite:///tasks.db"
engine = create_engine(DATABASE_URL, echo=False)
SQLModel.metadata.create_all(engine)

# -------------------- FastAPI App --------------------
app = FastAPI(title="AI Task Manager Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- CRUD --------------------
def create_task(task: Task) -> Task:
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

def get_tasks() -> List[Task]:
    with Session(engine) as session:
        return session.exec(select(Task)).all()

def update_task(task_id: int, updates: dict) -> Task:
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        session.commit()
        session.refresh(task)
        return task

def delete_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        session.delete(task)
        session.commit()

def bulk_update_tasks(task_ids: List[int], updates: dict):
    with Session(engine) as session:
        for task_id in task_ids:
            task = session.get(Task, task_id)
            if task:
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
        session.commit()

# -------------------- API Endpoints --------------------
@app.post("/tasks", response_model=TaskRead)
def add_task(task: Task):
    try:
        return create_task(task)
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        raise HTTPException(status_code=500, detail="Failed to add task")

@app.get("/tasks", response_model=List[TaskRead])
def list_tasks():
    try:
        return get_tasks()
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to list tasks")

@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_task_endpoint(task_id: int, updates: dict = Body(...)):
    try:
        return update_task(task_id, updates)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update task")

@app.delete("/tasks/{task_id}")
def delete_task_endpoint(task_id: int):
    try:
        delete_task(task_id)
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete task")

@app.put("/tasks/bulk")
def bulk_update_endpoint(task_ids: List[int] = Body(..., embed=True), updates: dict = Body(..., embed=True)):
    try:
        bulk_update_tasks(task_ids, updates)
        return {"message": "Bulk update successful"}
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        raise HTTPException(status_code=500, detail="Failed to bulk update tasks")

# -------------------- AI Suggestions --------------------
async def groq_generate_plain(prompt: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    enhanced_prompt = f"Based on this work: '{prompt}', suggest 3-5 actionable tasks as Title: Description (Priority X)."
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are an AI task assistant."},
            {"role": "user", "content": enhanced_prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Groq API Error: {resp.text}")
    data = resp.json()
    content = re.sub(r'\[.*\]', '', data["choices"][0]["message"]["content"], flags=re.DOTALL).strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    tasks = []
    for line in lines:
        if ':' in line:
            title, rest = line.split(':', 1)
            priority_match = re.search(r'\(Priority (\d)\)', rest)
            priority = int(priority_match.group(1)) if priority_match else 3
            description = re.sub(r'\(Priority \d\)', '', rest).strip()
            tasks.append({"title": title.strip(), "description": description, "priority": priority})
        else:
            tasks.append({"title": "Suggestion", "description": line, "priority": 3})
    return {"suggestions": tasks}

@app.post("/suggest")
async def suggest_plain(body: dict = Body(...)):
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Missing or empty 'text'")
    return await groq_generate_plain(text)
