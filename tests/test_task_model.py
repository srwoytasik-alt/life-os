from models.task import Task
from datetime import date, timedelta


def test_toggle_changes_completion():
    task = Task(1, "Test", "High", None, "General")
    assert task.completed is False

    task.toggle()
    assert task.completed is True


def test_is_overdue_true():
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    task = Task(1, "Test", "High", yesterday, "General")

    assert task.is_overdue() is True


def test_is_overdue_false_if_completed():
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    task = Task(1, "Test", "High", yesterday, "General", completed=True)

    assert task.is_overdue() is False
    