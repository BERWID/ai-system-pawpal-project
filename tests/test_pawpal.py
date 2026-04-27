"""tests/test_pawpal.py — automated test suite for PawPal+ core + AI guardrails."""

import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler
from ai_scheduler import validate_task_input, validate_task_list, AISchedulerAgent


# ── Task tests ───────────────────────────────────────────────────────────────

def test_task_mark_complete():
    task = Task(description="Walk", time="08:00 AM", frequency="daily")
    assert not task.completed
    task.mark_complete()
    assert task.completed


def test_task_reset():
    task = Task(description="Feed", time="07:00 AM", frequency="daily")
    task.mark_complete()
    task.reset()
    assert not task.completed


def test_task_next_occurrence_daily():
    today = date.today()
    task = Task(description="Walk", time="08:00 AM", frequency="daily", due_date=today)
    next_task = task.next_occurrence()
    assert next_task.due_date == today + timedelta(days=1)


def test_task_next_occurrence_weekly():
    today = date.today()
    task = Task(description="Bath", time="10:00 AM", frequency="weekly", due_date=today)
    next_task = task.next_occurrence()
    assert next_task.due_date == today + timedelta(weeks=1)


# ── Pet tests ─────────────────────────────────────────────────────────────────

def test_pet_add_task():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", "08:00 AM", "daily"))
    assert len(pet.tasks) == 1


def test_pet_remove_task():
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task("Walk", "08:00 AM", "daily"))
    pet.remove_task("Walk")
    assert len(pet.tasks) == 0


def test_pet_get_pending_tasks():
    pet = Pet(name="Mochi", species="dog", age=3)
    t1 = Task("Walk", "08:00 AM", "daily")
    t2 = Task("Feed", "07:00 AM", "daily")
    t2.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    pending = pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].description == "Walk"


# ── Scheduler tests ───────────────────────────────────────────────────────────

def _make_scheduler():
    owner = Owner("Jordan", "jordan@example.com")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", "08:00 AM", "daily"))
    pet.add_task(Task("Feed", "07:00 AM", "daily"))
    pet.add_task(Task("Meds", "12:00 PM", "daily"))
    owner.add_pet(pet)
    return Scheduler(owner), pet


def test_schedule_sorted_by_time():
    scheduler, _ = _make_scheduler()
    schedule = scheduler.get_todays_schedule()
    times = [t.time for _, t in schedule]
    assert times == sorted(times), "Tasks should be in chronological order"


def test_complete_task_marks_done():
    scheduler, pet = _make_scheduler()
    result = scheduler.complete_task("Mochi", "Walk")
    assert result is True
    walk = next(t for t in pet.tasks if t.description == "Walk" and t.completed)
    assert walk.completed


def test_complete_task_adds_recurrence():
    scheduler, pet = _make_scheduler()
    initial_count = len(pet.tasks)
    scheduler.complete_task("Mochi", "Feed")
    assert len(pet.tasks) == initial_count + 1


def test_detect_conflicts():
    owner = Owner("Jordan", "jordan@example.com")
    pet = Pet("Mochi", "dog", 3)
    pet.add_task(Task("Walk", "08:00 AM", "daily"))
    pet.add_task(Task("Bath", "08:00 AM", "weekly"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "08:00 AM" in conflicts[0]


def test_no_conflicts_different_times():
    scheduler, _ = _make_scheduler()
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 0


def test_filter_by_completion():
    scheduler, pet = _make_scheduler()
    scheduler.complete_task("Mochi", "Walk")
    done = scheduler.filter_tasks(completed=True)
    assert all(t.completed for _, t in done)


# ── Guardrail tests ───────────────────────────────────────────────────────────

def test_guardrail_valid_input():
    ok, _ = validate_task_input("Morning walk", 30, "dog")
    assert ok


def test_guardrail_blocked_term():
    ok, reason = validate_task_input("Harm the pet", 30, "dog")
    assert not ok
    assert "disallowed" in reason.lower()


def test_guardrail_duration_too_long():
    ok, reason = validate_task_input("Walk", 999, "dog")
    assert not ok
    assert "Duration" in reason


def test_guardrail_bad_species():
    ok, reason = validate_task_input("Walk", 30, "dragon")
    assert not ok
    assert "species" in reason.lower()


def test_guardrail_task_list_too_large():
    tasks = [{"title": f"Task {i}"} for i in range(25)]
    ok, reason = validate_task_list(tasks)
    assert not ok
    assert "Too many" in reason


def test_guardrail_short_title():
    ok, reason = validate_task_input("A", 30, "cat")
    assert not ok


# ── AI agent (no-key stub) ────────────────────────────────────────────────────

def test_agent_no_key_returns_error():
    agent = AISchedulerAgent(api_key="")
    result = agent.recommend_schedule("Mochi", "dog", 3, [{"title": "Walk"}])
    assert "error" in result


def test_agent_stats_zero_calls():
    agent = AISchedulerAgent(api_key="")
    stats = agent.stats()
    assert stats["api_calls"] == 0
    assert stats["success_rate"] == 1.0