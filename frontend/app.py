import streamlit as st
import requests
from datetime import datetime, time
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Refresh every 60 seconds (60,000 ms)
st_autorefresh(interval=60_000, key="reminder_refresh")


# ---------------------- Backend URL ----------------------
BACKEND_URL = "http://127.0.0.1:8000"

# ---------------------- Page Config ----------------------
st.set_page_config(page_title="AI Task Manager", layout="wide")
st.title("📝 AI Task Manager Agent")

# ---------------------- Session State ----------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = {}
if "edit_task_id" not in st.session_state:
    st.session_state.edit_task_id = None
if "refresh" not in st.session_state:
    st.session_state.refresh = False  # used to trigger refresh

# ---------------------- Helper Functions ----------------------
def load_tasks():
    try:
        r = requests.get(f"{BACKEND_URL}/tasks")
        if r.status_code == 200:
            st.session_state.tasks = r.json()
        else:
            st.error(f"❌ Error loading tasks: {r.text}")
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Backend not reachable at {BACKEND_URL}. Please ensure your backend is running.")
    except Exception as e:
        st.error(f"❌ Unexpected error loading tasks: {str(e)}")

def parse_time_input(time_str: str) -> time:
    time_str = time_str.strip()
    try:
        return datetime.strptime(time_str, "%I:%M %p").time()
    except ValueError:
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            st.warning("Invalid time format. Defaulting to current time.")
            return datetime.now().time()

def check_reminders():
    now = datetime.now()
    for task in st.session_state.tasks:
        if task.get("set_reminder") and not task.get("completed") and task.get("reminder_time"):
            reminder_time = datetime.fromisoformat(task["reminder_time"])
            if 0 <= (now - reminder_time).total_seconds() <= 60:
                st.warning(f"⏰ Reminder: {task['title']}")

def trigger_refresh():
    st.session_state['refresh'] = not st.session_state['refresh']

# ---------------------- Load tasks initially ----------------------
if not st.session_state.tasks:
    load_tasks()

# ---------------------- Tabs ----------------------
tab1, tab2 = st.tabs(["📋 Tasks", "🤖 AI Suggestions"])

# ---------------------- TAB 1: TASKS ----------------------
with tab1:
    st.header("➕ Add a New Task")
    with st.expander("Click to Add Task"):
        with st.form("add_task_form", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                title = st.text_input("Task Title")
            with col2:
                priority = st.select_slider("Priority", options=range(1,6), value=3)

            description = st.text_area("Description")
            col3, col4, col5 = st.columns(3)
            with col3:
                reminder_date = st.date_input("Reminder Date", value=datetime.now().date())
            with col4:
                reminder_time = st.text_input("Reminder Time", placeholder="e.g., 2:30 PM or 14:30", value="12:00 PM")
            with col5:
                set_reminder = st.checkbox("Set Reminder", value=True)
            
            submitted = st.form_submit_button("✅ Add Task")

        if submitted:
            if not title or not description:
                st.error("Title and Description are required.")
            else:
                try:
                    parsed_time = parse_time_input(reminder_time)
                    reminder_datetime = datetime.combine(reminder_date, parsed_time).isoformat() if set_reminder else None
                    payload = {
                        "title": title,
                        "description": description,
                        "reminder_time": reminder_datetime,
                        "priority": priority,
                        "completed": False,
                        "set_reminder": set_reminder
                    }
                    r = requests.post(f"{BACKEND_URL}/tasks", json=payload)
                    if r.status_code == 200:
                        st.success("✅ Task added successfully!")
                        trigger_refresh()  # refresh Streamlit
                    else:
                        st.error(f"❌ Error adding task: {r.text}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")

    st.header("📋 Your Tasks")
    col_sort, col_filter = st.columns(2)
    with col_sort:
        sort_by = st.selectbox("Sort by", ["Priority", "Reminder Date", "Status"], index=0)
    with col_filter:
        search = st.text_input("Search tasks")

    if st.button("🔄 Refresh Tasks"):
        load_tasks()
        trigger_refresh()

    tasks = st.session_state.tasks
    if search:
        tasks = [t for t in tasks if search.lower() in t['title'].lower() or search.lower() in t['description'].lower()]
    if sort_by == "Priority":
        tasks = sorted(tasks, key=lambda x: x['priority'])
    elif sort_by == "Reminder Date":
        tasks = sorted(tasks, key=lambda x: x.get('reminder_time',''))
    elif sort_by == "Status":
        tasks = sorted(tasks, key=lambda x: x['completed'])

    if tasks:
        for task in tasks:
            completed = task['completed']
            style = "text-decoration: line-through; color:gray;" if completed else ""
            reminder_str = datetime.fromisoformat(task['reminder_time']).strftime("%Y-%m-%d %I:%M %p") if task['reminder_time'] else "No reminder set"
            status_text = "🟢 Completed" if completed else "🔴 Pending"
            priority_icon = "🔥" if task['priority']==1 else ("⚠️" if task['priority']==2 else "➡️")

            with st.container():
                st.markdown(f"<h4 style='{style}'>{priority_icon} {task['title']}</h4>", unsafe_allow_html=True)
                st.write(f"**Status:** {status_text}")
                st.caption(f"📅 Reminder: {reminder_str} | Priority: {task['priority']}")
                
                col1, col2, col3 = st.columns(3)
                
                # Mark Complete
                with col1:
                    if not completed:
                        if st.button("✅ Mark Complete", key=f"complete_{task['id']}"):
                            try:
                                r = requests.put(f"{BACKEND_URL}/tasks/{task['id']}", json={"completed": True})
                                if r.status_code == 200:
                                    st.success("Task marked complete!")
                                    trigger_refresh()
                                else:
                                    st.error(f"Error: {r.text}")
                            except Exception as e:
                                st.error(f"Unexpected error: {str(e)}")

                # Edit Task
                with col2:
                    if st.session_state.edit_task_id == task['id']:
                        with st.form(f"edit_form_{task['id']}", clear_on_submit=False):
                            new_title = st.text_input("Title", value=task['title'])
                            new_desc = st.text_area("Description", value=task['description'])
                            new_priority = st.select_slider("Priority", options=range(1,6), value=task['priority'])
                            new_reminder_date = st.date_input(
                                "Reminder Date",
                                value=datetime.fromisoformat(task['reminder_time']).date() if task['reminder_time'] else datetime.now().date()
                            )
                            new_reminder_time = st.text_input(
                                "Reminder Time",
                                value=datetime.fromisoformat(task['reminder_time']).strftime("%I:%M %p") if task['reminder_time'] else "12:00 PM"
                            )
                            new_set_reminder = st.checkbox("Set Reminder", value=task['set_reminder'])
                            save = st.form_submit_button("💾 Save Changes")
                            if save:
                                if not new_title or not new_desc:
                                    st.error("Title and Description are required.")
                                else:
                                    try:
                                        parsed_time = parse_time_input(new_reminder_time)
                                        new_reminder_datetime = datetime.combine(new_reminder_date, parsed_time).isoformat()
                                        updates = {
                                            "title": new_title,
                                            "description": new_desc,
                                            "priority": new_priority,
                                            "reminder_time": new_reminder_datetime,
                                            "set_reminder": new_set_reminder
                                        }
                                        r = requests.put(f"{BACKEND_URL}/tasks/{task['id']}", json=updates)
                                        if r.status_code == 200:
                                            st.success("Task updated successfully!")
                                            st.session_state.edit_task_id = None
                                            trigger_refresh()
                                        else:
                                            st.error(f"Error: {r.text}")
                                    except Exception as e:
                                        st.error(f"Unexpected error: {str(e)}")
                    else:
                        if not completed and st.button("✏️ Edit", key=f"edit_btn_{task['id']}"):
                            st.session_state.edit_task_id = task['id']

                # Delete Task
                with col3:
                    confirm_key = f"delete_{task['id']}"
                    if st.button("🗑️ Delete", key=confirm_key):
                        st.session_state.confirm_delete[confirm_key] = True
                    if st.session_state.confirm_delete.get(confirm_key, False):
                        st.warning("Are you sure?")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("Yes", key=f"yes_{task['id']}"):
                                try:
                                    r = requests.delete(f"{BACKEND_URL}/tasks/{task['id']}")
                                    if r.status_code==200:
                                        st.success("Task deleted!")
                                        st.session_state.confirm_delete[confirm_key]=False
                                        trigger_refresh()
                                    else:
                                        st.error(f"Error: {r.text}")
                                except Exception as e:
                                    st.error(f"Unexpected error: {str(e)}")
                        with c2:
                            if st.button("Cancel", key=f"cancel_{task['id']}"):
                                st.session_state.confirm_delete[confirm_key]=False
                                st.info("Cancelled")
    else:
        st.info("No tasks found. Add one above!")

    # Check reminders
    check_reminders()

# ------------------ TAB 2: AI SUGGESTIONS ------------------
with tab2:
    st.header("🤖 AI Task Suggestions")
    with st.expander("Get Suggestions based on your work"):
        prompt = st.text_area(
            "Describe your current work", height=150,
            placeholder="e.g., Working on DB migration, auth refactor..."
        )

        if st.button("🧠 Get Suggestions", type="primary"):
            if prompt.strip():
                try:
                    r = requests.post(f"{BACKEND_URL}/suggest", json={"text": prompt})
                    if r.status_code == 200:
                        data = r.json()
                        suggestions = data.get("suggestions", [])
                        if suggestions:
                            st.success("✨ AI Suggestions:\n")
                            for sug in suggestions:
                                title = sug.get("title", "No Title")
                                desc = sug.get("description", "No Description")
                                st.markdown(f"**{title}:** {desc}\n")
                        else:
                            st.info("No suggestions received.")
                    else:
                        st.error(f"Error from backend: {r.text}")
                except requests.exceptions.ConnectionError:
                    st.error(f"❌ Backend not reachable at {BACKEND_URL}. Please ensure your backend is running.")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
            else:
                st.warning("Please enter your current work description to get suggestions.")
