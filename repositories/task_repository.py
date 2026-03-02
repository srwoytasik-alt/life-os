# repositories/task_repository.py

import json
from models.task import Task


class TaskRepository:
    def __init__(self, filepath):
        self.filepath = filepath
        self.tasks = self.load()

    def load(self):
        try:
            with open(self.filepath, "r") as file:
                data = json.load(file)
            return [Task(**item) for item in data]
        except FileNotFoundError:
            return []

    def save(self):
        with open(self.filepath, "w") as file:
            json.dump([t.to_dict() for t in self.tasks], file, indent=4)

    def get_all(self):
        return self.tasks

    def add(self, title, priority, due_date, domain):
        new_id = max((t.id for t in self.tasks), default=0) + 1
        new_task = Task(new_id, title, priority, due_date, domain)
        self.tasks.append(new_task)
        self.save()

    def toggle(self, task_id):
        for t in self.tasks:
            if t.id == task_id:
                t.toggle()
                break
        self.save()

    def delete(self, task_id):
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.save()
        