import streamlit as st
from pawpal_system import Owner, Pet, Scheduler, Task
from ai_helper import get_schedule_advice, check_welfare, validate_input

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

for key, val in [("tasks", []), ("owner", None)]:
    if key not in st.session_state:
        st.session_state[key] = val

with st.sidebar:
    gemini_key = st.text_input("Gemini API key", type="password")

st.subheader("Owner & Pet")
col1, col2, col3 = st.columns(3)
owner_name = col1.text_input("Owner name", value="Jordan")
pet_name = col2.text_input("Pet name", value="Mochi")
species = col3.selectbox("Species", ["dog", "cat", "other"])

st.subheader("Tasks")
col1, col2, col3, col4 = st.columns(4)
task_title = col1.text_input("Task title", value="Morning walk")
duration = col2.number_input("Duration (min)", min_value=1, max_value=480, value=20)
priority = col3.selectbox("Priority", ["low", "medium", "high"], index=2)
task_time = col4.text_input("Time (HH:MM AM/PM)", value="08:00 AM")

if st.button("Add task"):
    ok, reason = validate_input(task_title, int(duration))
    if not ok:
        st.error(f"Blocked: {reason}")
    else:
        st.session_state.tasks.append(
            {"title": task_title, "duration_minutes": int(duration), "priority": priority, "time": task_time}
        )

if st.session_state.tasks:
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet.")

st.divider()
st.subheader("Generate Schedule")
if st.button("Build schedule"):
    if not st.session_state.tasks:
        st.warning("Add tasks first.")
    else:
        owner = Owner(name=owner_name, email="owner@example.com")
        pet = Pet(name=pet_name, species=species, age=3)
        for t in st.session_state.tasks:
            freq = "daily" if t["priority"] == "high" else "weekly"
            pet.add_task(Task(description=t["title"], time=t["time"], frequency=freq))
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        for c in scheduler.detect_conflicts():
            st.warning(f"⚠️ {c}")
        schedule = scheduler.get_todays_schedule()
        st.success(f"{len(schedule)} task(s) scheduled for {pet_name}")
        for _, task in schedule:
            st.write(f"{'✅' if task.completed else '🔲'} **{task.time}** — {task.description}")

st.divider()
st.subheader("🤖 AI Assistant (Gemini)")

if st.button("Get AI schedule advice"):
    if not gemini_key:
        st.error("Enter your Gemini API key in the sidebar.")
    elif not st.session_state.tasks:
        st.warning("Add tasks first.")
    else:
        with st.spinner("Asking Gemini..."):
            advice = get_schedule_advice(gemini_key, pet_name, species, st.session_state.tasks)
        st.info(advice)

if st.button("Check animal welfare"):
    if not gemini_key:
        st.error("Enter your Gemini API key in the sidebar.")
    elif not st.session_state.tasks:
        st.warning("Add tasks first.")
    else:
        with st.spinner("Checking..."):
            result = check_welfare(gemini_key, pet_name, species, st.session_state.tasks)
        st.warning(result)
