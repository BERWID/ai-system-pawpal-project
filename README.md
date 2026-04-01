# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Enter owner and pet info in a simple UI
- Add tasks with title, duration, priority, and scheduled time
- Generate a sorted daily schedule based on time and priority
- Conflict warnings when two tasks are scheduled at the same time
- Daily/weekly recurrence — completing a task auto-schedules the next occurrence
- Full test suite covering core scheduling behaviors

## Getting started


### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
### Run the app

```bash
streamlit run app.py
```

## Smarter Scheduling

The `Scheduler` class handles all algorithmic logic:
- Tasks sorted using Python's `sorted()` with a time-string key
- Conflict detection scans for duplicate time slots across all pets
- Recurrence uses `timedelta` to calculate the next due date on task completion
- Filtering supports both pet name and completion status

## Testing PawPal+

```bash
pip install pytest
python -m pytest
```

**Tests cover:**
- Task completion (`mark_complete()` flips status correctly)
- Task addition increases pet task count
- Sorting correctness — tasks returned in chronological order
- Recurrence logic — completing a daily task adds a new task due tomorrow
- Conflict detection — scheduler flags two tasks at the same time

## 📸 Demo
<a href="/screenshot.png" target="_blank"><img src='/screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>
## System Architecture

See `uml_final.png` for the final class diagram.

## Project Structure

```
pawpal_system.py   # Logic layer — Task, Pet, Owner, Scheduler classes
app.py             # Streamlit UI
main.py            # CLI demo script
tests/
  test_pawpal.py   # Automated test suite
reflection.md      # Design decisions and AI strategy
uml_final.png      # Final UML class diagram
README.md
```
### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
