from datetime import date

import pytest

from project import (
    build_daily_plan,
    calculate_priority,
    create_task,
    format_task,
    normalize_subject,
    parse_due_date,
    sort_tasks_by_priority,
)


def test_normalize_subject():
    assert normalize_subject("  data   analytics ") == "Data Analytics"
    assert normalize_subject("PYTHON") == "Python"
    with pytest.raises(ValueError):
        normalize_subject("   ")


def test_parse_due_date():
    assert parse_due_date("2026-06-16") == date(2026, 6, 16)
    with pytest.raises(ValueError):
        parse_due_date("06/16/2026")


def test_calculate_priority():
    today = date(2026, 6, 10)
    urgent = calculate_priority("2026-06-10", 3, 2, today=today)
    later = calculate_priority("2026-06-20", 3, 2, today=today)
    assert urgent > later
    with pytest.raises(ValueError):
        calculate_priority("2026-06-16", 6, 2, today=today)
    with pytest.raises(ValueError):
        calculate_priority("2026-06-16", 3, 0, today=today)


def test_create_task():
    task = create_task(
        "python",
        "finish final project",
        "2026-06-16",
        4,
        3,
        today=date(2026, 6, 10),
    )
    assert task["subject"] == "Python"
    assert task["description"] == "finish final project"
    assert task["due_date"] == "2026-06-16"
    assert task["difficulty"] == 4
    assert task["estimated_hours"] == 3.0
    assert task["completed"] is False
    assert task["priority"] > 0


def test_sort_tasks_by_priority():
    today = date(2026, 6, 10)
    tasks = [
        create_task("History", "read chapter", "2026-06-30", 2, 1, today=today),
        create_task("Python", "submit project", "2026-06-11", 5, 5, today=today),
    ]
    sorted_tasks = sort_tasks_by_priority(tasks, today=today)
    assert sorted_tasks[0]["subject"] == "Python"


def test_build_daily_plan():
    today = date(2026, 6, 10)
    tasks = [
        create_task("Python", "submit project", "2026-06-11", 5, 2, today=today),
        create_task("Math", "practice problems", "2026-06-12", 3, 4, today=today),
    ]
    plan = build_daily_plan(tasks, 3)
    assert len(plan) == 1
    assert plan[0]["subject"] == "Python"
    with pytest.raises(ValueError):
        build_daily_plan(tasks, 0)


def test_format_task():
    task = create_task("Python", "test app", "2026-06-16", 3, 2, today=date(2026, 6, 10))
    text = format_task(task, 1)
    assert "1." in text
    assert "Python" in text
    assert "test app" in text
    assert "Open" in text
