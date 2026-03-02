from database import db
from models.task_model import TaskModel


def test_insert_task(app):
    with app.app_context():
        task = TaskModel(
            title="DB Test",
            priority="High",
            domain="General",
            completed=False
        )

        db.session.add(task)
        db.session.commit()

        assert TaskModel.query.count() == 1
        