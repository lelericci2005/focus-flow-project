"""FocusFlow Study Planner

A small command-line study planner that helps students organize assignments,
rank tasks by urgency, and build a realistic daily study plan.
"""

import json
from datetime import date, datetime
from pathlib import Path

TASKS_FILE = "tasks.json"


def normalize_subject(subject):
    """Return a clean, title-cased subject name.

    Args:
        subject (str): The subject typed by the user.

    Returns:
        str: The cleaned subject.

    Raises:
        ValueError: If the subject is empty.
    """
    cleaned = " ".join(str(subject).strip().split())
    if not cleaned:
        raise ValueError("Subject cannot be empty.")
    return cleaned.title()


def parse_due_date(date_text):
    """Convert a YYYY-MM-DD string into a date object.

    Args:
        date_text (str): The due date as text.

    Returns:
        date: A Python date object.

    Raises:
        ValueError: If the date is not in the correct format.
    """
    try:
        return datetime.strptime(str(date_text).strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Due date must be in YYYY-MM-DD format.") from exc


def calculate_priority(due_date, difficulty, estimated_hours, today=None):
    """Calculate a priority score for a task.

    The score combines urgency, difficulty, and estimated time. A task due soon
    receives a higher score. A difficult or long task also receives a higher
    score because it needs more attention.

    Args:
        due_date (date | str): Due date as a date object or YYYY-MM-DD string.
        difficulty (int): Difficulty from 1 to 5.
        estimated_hours (float): Estimated time needed.
        today (date, optional): Used for testing. Defaults to today's date.

    Returns:
        float: Priority score rounded to two decimals.

    Raises:
        ValueError: If difficulty or estimated hours are invalid.
    """
    if today is None:
        today = date.today()

    if isinstance(due_date, str):
        due_date = parse_due_date(due_date)

    try:
        difficulty = int(difficulty)
    except (TypeError, ValueError) as exc:
        raise ValueError("Difficulty must be a number from 1 to 5.") from exc

    try:
        estimated_hours = float(estimated_hours)
    except (TypeError, ValueError) as exc:
        raise ValueError("Estimated hours must be a number.") from exc

    if difficulty < 1 or difficulty > 5:
        raise ValueError("Difficulty must be between 1 and 5.")
    if estimated_hours <= 0:
        raise ValueError("Estimated hours must be greater than 0.")

    days_left = max((due_date - today).days, 0)
    urgency_score = 100 / (days_left + 1)
    difficulty_score = difficulty * 7
    time_score = estimated_hours * 2

    return round(urgency_score + difficulty_score + time_score, 2)


def create_task(subject, description, due_date, difficulty, estimated_hours, today=None):
    """Create and return a task dictionary.

    Args:
        subject (str): School subject or course name.
        description (str): Short task description.
        due_date (date | str): Due date.
        difficulty (int): Difficulty from 1 to 5.
        estimated_hours (float): Estimated time needed.
        today (date, optional): Used for testing.

    Returns:
        dict: A task with all required information.
    """
    if isinstance(due_date, str):
        due_date = parse_due_date(due_date)

    subject = normalize_subject(subject)
    description = " ".join(str(description).strip().split())
    if not description:
        raise ValueError("Description cannot be empty.")

    priority = calculate_priority(due_date, difficulty, estimated_hours, today=today)

    return {
        "subject": subject,
        "description": description,
        "due_date": due_date.isoformat(),
        "difficulty": int(difficulty),
        "estimated_hours": float(estimated_hours),
        "priority": priority,
        "completed": False,
    }


def sort_tasks_by_priority(tasks, today=None):
    """Return tasks sorted by priority, with unfinished tasks first.

    Args:
        tasks (list): List of task dictionaries.
        today (date, optional): Used for testing.

    Returns:
        list: Sorted list of task dictionaries.
    """
    updated_tasks = []

    for task in tasks:
        copied_task = task.copy()
        if not copied_task.get("completed", False):
            copied_task["priority"] = calculate_priority(
                copied_task["due_date"],
                copied_task["difficulty"],
                copied_task["estimated_hours"],
                today=today,
            )
        updated_tasks.append(copied_task)

    return sorted(
        updated_tasks,
        key=lambda task: (task.get("completed", False), -task.get("priority", 0)),
    )


def build_daily_plan(tasks, available_hours):
    """Build a study plan that fits inside the available hours.

    Args:
        tasks (list): List of task dictionaries.
        available_hours (float): Hours available to study today.

    Returns:
        list: Tasks selected for today's plan.

    Raises:
        ValueError: If available hours are invalid.
    """
    try:
        available_hours = float(available_hours)
    except (TypeError, ValueError) as exc:
        raise ValueError("Available hours must be a number.") from exc

    if available_hours <= 0:
        raise ValueError("Available hours must be greater than 0.")

    chosen_tasks = []
    used_hours = 0.0
    sorted_tasks = sort_tasks_by_priority(tasks)

    for task in sorted_tasks:
        if task.get("completed", False):
            continue
        hours = float(task["estimated_hours"])
        if used_hours + hours <= available_hours:
            chosen_tasks.append(task)
            used_hours += hours

    return chosen_tasks


def format_task(task, number=None):
    """Format a task as a readable string for the terminal.

    Args:
        task (dict): A task dictionary.
        number (int, optional): Display number.

    Returns:
        str: A formatted task.
    """
    prefix = f"{number}. " if number is not None else ""
    status = "Done" if task.get("completed", False) else "Open"
    return (
        f"{prefix}[{status}] {task['subject']} - {task['description']} | "
        f"Due: {task['due_date']} | Difficulty: {task['difficulty']}/5 | "
        f"Hours: {task['estimated_hours']} | Priority: {task['priority']}"
    )


def load_tasks(file_path=TASKS_FILE):
    """Load tasks from a JSON file.

    Args:
        file_path (str): Path to the JSON task file.

    Returns:
        list: Saved tasks, or an empty list if no file exists.
    """
    path = Path(file_path)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_tasks(tasks, file_path=TASKS_FILE):
    """Save tasks to a JSON file.

    Args:
        tasks (list): List of task dictionaries.
        file_path (str): Path to the JSON task file.
    """
    path = Path(file_path)
    with path.open("w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)


def add_task_menu(tasks):
    """Ask the user for task details and add a new task."""
    print("\nAdd a new task")
    subject = input("Subject/course: ")
    description = input("Task description: ")
    due_date = input("Due date (YYYY-MM-DD): ")
    difficulty = input("Difficulty (1-5): ")
    estimated_hours = input("Estimated hours needed: ")

    try:
        task = create_task(subject, description, due_date, difficulty, estimated_hours)
        tasks.append(task)
        print("Task added successfully.")
    except ValueError as error:
        print(f"Could not add task: {error}")


def view_tasks_menu(tasks):
    """Print all tasks to the terminal."""
    if not tasks:
        print("\nNo tasks yet.")
        return

    print("\nYour tasks")
    for index, task in enumerate(sort_tasks_by_priority(tasks), start=1):
        print(format_task(task, index))


def complete_task_menu(tasks):
    """Allow the user to mark a task as completed."""
    if not tasks:
        print("\nNo tasks to complete.")
        return

    view_tasks_menu(tasks)
    try:
        choice = int(input("\nWhich task number did you complete? "))
        sorted_tasks = sort_tasks_by_priority(tasks)
        selected_task = sorted_tasks[choice - 1]
    except (ValueError, IndexError):
        print("Invalid task number.")
        return

    for task in tasks:
        if (
            task["subject"] == selected_task["subject"]
            and task["description"] == selected_task["description"]
            and task["due_date"] == selected_task["due_date"]
        ):
            task["completed"] = True
            print("Task marked as completed.")
            return


def daily_plan_menu(tasks):
    """Ask for available hours and show a daily study plan."""
    if not tasks:
        print("\nNo tasks available for a plan.")
        return

    try:
        available_hours = input("How many hours can you study today? ")
        plan = build_daily_plan(tasks, available_hours)
    except ValueError as error:
        print(f"Could not build plan: {error}")
        return

    if not plan:
        print("No task fits into your available study time today.")
        return

    print("\nToday's study plan")
    for index, task in enumerate(plan, start=1):
        print(format_task(task, index))


def main():
    """Run the FocusFlow Study Planner menu."""
    tasks = load_tasks()

    while True:
        print("\nFocusFlow Study Planner")
        print("1. Add task")
        print("2. View tasks")
        print("3. Mark task completed")
        print("4. Build today's study plan")
        print("5. Save and exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_task_menu(tasks)
        elif choice == "2":
            view_tasks_menu(tasks)
        elif choice == "3":
            complete_task_menu(tasks)
        elif choice == "4":
            daily_plan_menu(tasks)
        elif choice == "5":
            save_tasks(tasks)
            print("Tasks saved. Goodbye!")
            break
        else:
            print("Please choose a number from 1 to 5.")


if __name__ == "__main__":
    main()
