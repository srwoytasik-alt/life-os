from repositories.task_repository import TaskRepository
import os


def test_add_task_creates_new_task(tmp_path):
    test_file = tmp_path / "tasks.json"
    repo = TaskRepository(test_file)

    repo.add("Test", "High", None, "General")

    assert len(repo.get_all()) == 1
    assert repo.get_all()[0].title == "Test"


def test_delete_task_removes_task(tmp_path):
    test_file = tmp_path / "tasks.json"
    repo = TaskRepository(test_file)

    repo.add("Test", "High", None, "General")
    repo.delete(1)

    assert len(repo.get_all()) == 0
    