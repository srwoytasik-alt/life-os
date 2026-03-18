# app.py

import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import db, migrate
from config import Config
from models.task_model import TaskModel
from services.task_service import TaskService
from repositories.sql_repository import SQLTaskRepository
from services.reminder_service import check_due_tasks
from datetime import datetime

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure instance folder exists
    try:
        os.makedirs(os.path.join(os.path.dirname(__file__), 'instance'), exist_ok=True)
    except OSError:
        pass
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Initialize repository and service
    repo = SQLTaskRepository()
    task_service = TaskService(repo)
    
    @app.route('/')
    def index():
        filter_type = request.args.get('filter', 'all')
        tasks = task_service.get_filtered_tasks(filter_type)
        
        # Get suggestions for today
        suggestions = task_service.get_suggestions()
        
        # Calculate stats
        total_tasks = len(task_service.get_all())
        completed_tasks = len([t for t in task_service.get_all() if t.completed])
        completion_percentage = round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0
        
        # Calculate urgency percentage (Critical + High incomplete)
        critical_high = len([t for t in task_service.get_all() 
                            if not t.completed and t.priority in ['Critical', 'High']])
        urgency_percentage = round((critical_high / total_tasks * 100), 2) if total_tasks > 0 else 0
        
        # Stability index
        stability = task_service.get_stability_index()
        
        # Today's mission
        todays_mission = task_service.get_todays_mission()
        
        return render_template('index.html', 
                             tasks=tasks,
                             suggestions=suggestions,
                             completion_percentage=completion_percentage,
                             urgency_percentage=urgency_percentage,
                             stability=stability,
                             todays_mission=todays_mission,
                             current_filter=filter_type)
    
    @app.route('/add', methods=['POST'])
    def add_task():
        title = request.form.get('title')
        priority = request.form.get('priority', 'Medium')
        due_date = request.form.get('due_date')
        domain = request.form.get('domain', 'General')
        
        if title:
            task_service.add_task(title, priority, due_date, domain)
        
        return redirect(url_for('index'))
    
    @app.route('/toggle/<int:task_id>')
    def toggle_task(task_id):
        task_service.toggle(task_id)
        return redirect(url_for('index'))
    
    @app.route('/delete/<int:task_id>')
    def delete_task(task_id):
        task_service.delete(task_id)
        return redirect(url_for('index'))
    
    @app.route('/check-reminders')
    def check_reminders():
        with app.app_context():
            check_due_tasks()
        return redirect(url_for('index'))
    
    @app.route('/api/tasks')
    def api_tasks():
        tasks = task_service.get_all()
        return jsonify([{
            'id': t.id,
            'title': t.title,
            'priority': t.priority,
            'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None,
            'domain': t.domain,
            'completed': t.completed
        } for t in tasks])
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)