"""PawPal+ Logic Layer — core classes for the pet care scheduling system."""

from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str                        # e.g. "08:00 AM"
    frequency: str                   # e.g. "daily", "weekly"
    completed: bool = False

    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def reset(self) -> None:
        """Reset completion status for a new day."""
        self.completed = False

    def next_occurrence(self) -> "Task":
        """Return a new Task for the next occurrence based on frequency."""
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        return Task(self.description, self.time, self.frequency, due_date=self.due_date + delta)

    def __str__(self) -> str:
        status = "✓" if self.completed else "○"
        return f"[{status}] {self.time} — {self.description} ({self.frequency})"


@dataclass
class Pet:
    """Stores pet details and the list of tasks assigned to it."""

    name: str
    species: str                     # e.g. "dog", "cat"
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> None:
        """Remove a task by its description."""
        self.tasks = [t for t in self.tasks if t.description != description]

    def get_pending_tasks(self) -> list[Task]:
        """Return all incomplete tasks for this pet."""
        return [t for t in self.tasks if not t.completed]

    def __str__(self) -> str:
        return f"{self.name} ({self.species}, age {self.age})"


@dataclass
class Owner:
    """Manages an owner's profile and their collection of pets."""

    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.name != name]

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def __str__(self) -> str:
        return f"{self.name} ({len(self.pets)} pet(s))"


class Scheduler:
    """The brain of PawPal+: retrieves, sorts, and manages tasks across all pets."""

    def __init__(self, owner: Owner) -> None:
        """Initialize the scheduler with an owner."""
        self.owner = owner

    def get_todays_schedule(self) -> list[tuple[Pet, Task]]:
        """Return all tasks sorted by time."""
        all_tasks = self.owner.get_all_tasks()
        return sorted(all_tasks, key=lambda pt: pt[1].time)

    def get_pending(self) -> list[tuple[Pet, Task]]:
        """Return only incomplete tasks, sorted by time."""
        return [(pet, task) for pet, task in self.get_todays_schedule()
                if not task.completed]

    def complete_task(self, pet_name: str, description: str) -> bool:
        """Mark a specific task complete and schedule its next recurrence. Returns True if found."""
        for pet in self.owner.pets:
            if pet.name == pet_name:
                for task in pet.tasks:
                    if task.description == description and not task.completed:
                        task.mark_complete()
                        if task.frequency in ("daily", "weekly"):
                            pet.add_task(task.next_occurrence())
                        return True
        return False

    def filter_tasks(self, pet_name: str = None, completed: bool = None) -> list[tuple[Pet, Task]]:
        """Filter tasks by pet name and/or completion status."""
        results = self.get_todays_schedule()
        if pet_name:
            results = [(p, t) for p, t in results if p.name == pet_name]
        if completed is not None:
            results = [(p, t) for p, t in results if t.completed == completed]
        return results

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for any two tasks scheduled at the same time."""
        seen: dict[str, list[str]] = {}
        for pet, task in self.get_todays_schedule():
            seen.setdefault(task.time, []).append(pet.name)
        return [f"Conflict at {t}: {', '.join(pets)}" for t, pets in seen.items() if len(pets) > 1]

    def print_schedule(self) -> None:
        """Print today's full schedule to the terminal."""
        schedule = self.get_todays_schedule()
        if not schedule:
            print("No tasks scheduled for today.")
            return
        print(f"\n{'='*40}")
        print(f"  PawPal+ — Today's Schedule for {self.owner.name}")
        print(f"{'='*40}")
        for pet, task in schedule:
            print(f"  {pet.name:10s}  {task}")
        print(f"{'='*40}\n")