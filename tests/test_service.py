from services.task_service import TaskService
from models.task import Task


class FakeRepo:
    def __init__(self):
        self.tasks = []

    def get_all(self):
        return self.tasks

    def add(self, title, priority, due_date, domain):
        new_id = len(self.tasks) + 1
        self.tasks.append(Task(new_id, title, priority, due_date, domain))

    def toggle(self, task_id):
        for t in self.tasks:
            if t.id == task_id:
                t.toggle()

    def delete(self, task_id):
        self.tasks = [t for t in self.tasks if t.id != task_id]


def test_service_add():
    repo = FakeRepo()
    service = TaskService(repo)

    service.add_task("Test", "High", None, "General")

    assert len(repo.tasks) == 1


def test_service_toggle():
    repo = FakeRepo()
    service = TaskService(repo)

    service.add_task("Test", "High", None, "General")
    service.toggle(1)

    assert repo.tasks[0].completed is True
    