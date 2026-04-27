# PawPal+ AI

## Base Project

This extends **PawPal+** from Module 2. The original app let a pet owner register pets, add care tasks (walks, feeding, meds), detect scheduling conflicts, and generate a sorted daily plan using rule-based logic across four classes task, pet, owner and scheduler.

## New AI Features

**1. Gemini Schedule Advisor** — sends the owner's task list to Gemini and gets back a natural-language recommendation for the best task order and why. This is integrated directly into the Streamlit UI.

**2. Welfare Check** — sends the task list to Gemini and asks it to flag missing essential care or animal welfare concerns.

**3. Input Guardrail** — validates every task before it's added. Blocks empty titles, disallowed terms, and unrealistic durations. All decisions are logged to `pawpal.log`.

## Architecture

Data flow: User inputs task → guardrail validates → added to session → "Build schedule" sorts by time and detects conflicts → "Get AI advice" sends tasks to Gemini → response shown in UI.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Enter your Gemini API key in the sidebar when the app opens.

## WalkThrough + Sample Inputs & Outputs
https://drive.google.com/file/d/1UQ0KWmwobYg87umbB4Cw35U1XGbD2fQD/view?usp=sharing

Input 1 — Schedule advice:
Tasks: Morning walk (08:00 AM), Feeding (07:00 AM), Medication (12:00 PM) for a dog named Mochi.

"Start with feeding at 7 AM since dogs should eat before exercise. Follow with the morning walk at 8 AM once digestion has begun. Give medication at noon as scheduled — midday doses are easiest to remember and least disruptive to activity."

Input 2 — Welfare check:
Tasks: Morning walk only, for a dog.

"A single walk covers exercise but leaves feeding, water, and enrichment unaccounted for. Dogs need at least two meals daily and mental stimulation beyond physical exercise. Consider adding feeding and a play or training session."

Input 3 — Guardrail block:
Task title: "hurt the pet", duration: 999 minutes.

Blocked: "Task title contains a disallowed term." / "Duration must be 1–480 minutes."


## Testing

```bash
python -m pytest tests/ -v
```

These 21 tests cover task lifecycle, scheduler sorting, conflict detection, recurrence, and guardrail behavior.

## Files

```
pawpal_system.py   # Original core logic (unchanged)
ai_helper.py       # Gemini integration + guardrails
app.py             # Streamlit UI
tests/test_pawpal.py
reflection.md
requirements.txt
README.md
```