# app.py

from flask import Flask, render_template, request, redirect, jsonify
from config import Config
from database import db, migrate
from repositories.sql_repository import SQLTaskRepository
from services.task_service import TaskService
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from services.reminder_service import check_due_tasks
# from flask_mail import Mail, Message
import os
import models
from services.finance_service import FinanceService


def create_app(test_config=None):
    load_dotenv()

    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)
    else:
        app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register models with SQLAlchemy metadata
    import models  # Ensure models are registered here

    repo = SQLTaskRepository()
    service = TaskService(repo)
    finance_service = FinanceService()

    # # Configure Mail
    # app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
    # app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    # app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS")
    # app.config['MAIL_USE_SSL'] = os.getenv("MAIL_USE_SSL")
    # app.config['MAIL_PORT'] = os.getenv("MAIL_PORT")
    # app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")

    # mail = Mail(app)

    # # Send email reminder
    # def send_email_reminder(subject, body, to):
    #     msg = Message(subject, recipients=[to])
    #     msg.body = body
    #     mail.send(msg)

    # ---------------------
    # Web Routes
    # ---------------------

    @app.route("/")
    def index():
        operator = request.args.get("operator")

        if operator == "true":
            scored_tasks = service.get_top_critical()
        else:
            scored_tasks = service.get_ranked_tasks()

        # extract task list for stats
        tasks_only = [task for task, score in scored_tasks]

        total = len(tasks_only)
        completed = len([t for t in tasks_only if t.completed])

        completion_percent = round((completed / total) * 100, 2) if total else 0

        high_critical = len([t for t in tasks_only if t.priority in ["High", "Critical"]])
        urgency_percent = round((high_critical / total) * 100, 2) if total else 0

        suggestions = service.get_suggestions()
        stability_index = service.get_stability_index()

        return render_template(
            "index.html",
            scored_tasks=scored_tasks,
            suggested_tasks=suggestions,
            completion_percent=completion_percent,
            urgency_percent=urgency_percent,
            stability_index=stability_index
        )

    @app.route("/add", methods=["POST"])
    def add():
        service.add_task(
            request.form.get("title"),
            request.form.get("priority"),
            request.form.get("due_date"),
            request.form.get("domain")
        )
        return redirect("/")

    @app.route("/toggle/<int:task_id>")
    def toggle(task_id):
        service.toggle(task_id)
        return redirect("/")

    @app.route("/delete/<int:task_id>")
    def delete(task_id):
        service.delete(task_id)
        return redirect("/")

    # ---------------------
    # API Routes
    # ---------------------

    @app.route("/api/tasks", methods=["GET"])
    def api_get_tasks():
        tasks = service.get_all()
        return jsonify([t.to_dict() for t in tasks])

    @app.route("/api/tasks", methods=["POST"])
    def api_create_task():
        data = request.json

        service.add_task(
            data.get("title"),
            data.get("priority"),
            data.get("due_date"),
            data.get("domain")
        )

        return jsonify({"message": "Task created"}), 201

    @app.route("/import-finance", methods=["POST"])
    def import_finance():
        file = request.files["file"]
        filepath = "uploaded_finance.csv"
        file.save(filepath)

        finance_service.import_csv(filepath)

        return redirect("/")

    @app.route("/api/tasks/<int:task_id>", methods=["PUT"])
    def api_update_task(task_id):
        service.toggle(task_id)
        return jsonify({"message": "Task updated"})

    @app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
    def api_delete_task(task_id):
        service.delete(task_id)
        return jsonify({"message": "Task deleted"})

    # ---------------------
    # Background Scheduler
    # ---------------------

    # if not app.config.get("TESTING"):
    #     scheduler = BackgroundScheduler()

    #     def scheduled_job():
    #         with app.app_context():
    #             check_due_tasks()

    #     scheduler.add_job(
    #         func=scheduled_job,
    #         trigger="interval",
    #         minutes=1
    #     )

    #     scheduler.start()
        
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
    