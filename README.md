# AI Task Manager Agent

## Overview
AI Task Manager Agent is an AI-augmented task manager that helps users efficiently create, edit, delete, and prioritize tasks. It also provides AI-assisted task suggestions based on user input, allowing users to manage their work more effectively.

---

## Features
- Add, edit, delete tasks with priority levels  
- Set reminders for tasks  
- Track task completion status  
- Search and sort tasks  
- AI-powered task suggestions based on user input  

---

## Limitations
- AI suggestions are based on user-provided text only  
- Reminders require the app to be running  
- No voice input or external calendar integration  

---

## Tech Stack
- **Frontend:** Streamlit  
- **Backend:** FastAPI  
- **Database:** SQLite  
- **AI Module:** Groq API (similar to OpenAI GPT)  
- **Language:** Python  

---

## Setup Instructions

1. **Clone the repository**

git clone <repository_url>
cd AI-Task-Manager-Agent

2. **Install dependencies:**
pip install -r requirements.txt


3. **Set environment variables (Groq API key):**
Create a .env file:
GROQ_API_KEY=<your_api_key>

4. **Run the backend:**
uvicorn main:app --reload

5. **Run the frontend:**
streamlit run app.py


---

## Usage instructions
Explain how to use the app:
## Usage
- Tasks Tab: Add, edit, delete tasks, mark tasks as complete, search, and sort tasks.
- AI Suggestions Tab: Enter a description of your current work to get AI-generated task suggestions.
- Reminders appear if the app is running.

---

## Project Structure
AI-Task-Manager-Agent/
├─ app.py             # Streamlit frontend
├─ main.py            # FastAPI backend
├─ tasks.db           # SQLite database (auto-created)
├─ .env               # Environment variables 
├─ requirements.txt   # Python dependencies
└─ README.md          # Project documentation

---

## Future enhancements
- Voice input for tasks
- Calendar integration (Google Calendar)
- Push notifications for reminders
- More advanced AI suggestions with context

---

## Contact
For questions or suggestions, contact Me at deekshakotian928@gmail.com.
