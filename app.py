# app.py

import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from database import db, migrate
from config import Config
from models.task_model import TaskModel
from services.task_service import TaskService
from repositories.sql_repository import SQLTaskRepository
from services.reminder_service import check_due_tasks
from services.backup_service import backup_tasks_to_csv, get_last_backup_time
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool


def create_app(config_class=Config):
    app = Flask(__name__)
    
    # DEBUG: Print environment variables before loading config
    print("=" * 60)
    print("🔍 DEBUG - Environment Variables at Startup:")
    print("=" * 60)
    for key in os.environ:
        if 'DATABASE' in key or 'SUPABASE' in key:
            value = os.environ[key]
            if 'postgresql://' in value or 'postgres://' in value:
                # Mask the password for safety but show structure
                masked = value.split('@')
                if len(masked) > 1:
                    print(f"  {key}: {masked[0][:20]}...@{masked[1]}")
                else:
                    print(f"  {key}: [URL FORMAT]")
            else:
                print(f"  {key}: {value}")
    print("=" * 60)
    
    app.config.from_object(config_class)
    
    # DEBUG: Check what ended up in the config
    print(f"🔍 Config - SQLALCHEMY_DATABASE_URI after loading: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')}")
    
    # Ensure instance folder exists (for SQLite fallback)
    try:
        os.makedirs(os.path.join(os.path.dirname(__file__), 'instance'), exist_ok=True)
    except OSError:
        pass
    
    # Check if we're using Supabase (PostgreSQL) or SQLite
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
    
    if not database_url:
        print("❌ CRITICAL ERROR: SQLALCHEMY_DATABASE_URI is not set!")
        print("   Make sure SUPABASE_DATABASE_URL or DATABASE_URL is set in environment")
    else:
        using_supabase = 'supabase' in database_url.lower() or 'pooler.supabase' in database_url.lower()
        
        # Configure engine options based on database type
        if using_supabase:
            # For Supabase pooled connections, use NullPool
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'poolclass': NullPool,  # Let Supabase handle connection pooling
                'pool_pre_ping': True,
                'connect_args': {
                    'sslmode': 'require',
                    'connect_timeout': 10
                }
            }
            print("✅ Using Supabase PostgreSQL database")
        else:
            # For SQLite, use standard settings
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_pre_ping': True,
                'pool_recycle': 280
            }
            print("✅ Using SQLite database")
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created/verified")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
    
    # Initialize repository and service
    repo = SQLTaskRepository()
    task_service = TaskService(repo)
    
    # @app.route('/')
    # def index():
    #     filter_type = request.args.get('filter', 'all')
    #     show_archived = request.args.get('archived', 'false') == 'true'
        
    #     # Get tasks with archive filter
    #     if show_archived:
    #         tasks = task_service.get_archived_tasks()
    #     else:
    #         tasks = task_service.get_filtered_tasks(filter_type)
        
    #     # Get suggestions for today
    #     suggestions = task_service.get_suggestions()
        
    #     # Calculate stats
    #     all_tasks = task_service.get_all(include_archived=False)
    #     total_tasks = len(all_tasks)
    #     completed_tasks = len([t for t in all_tasks if t.completed])
    #     completion_percentage = round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0
        
    #     # Calculate urgency percentage (Critical + High incomplete)
    #     critical_high = len([t for t in all_tasks 
    #                         if not t.completed and t.priority in ['Critical', 'High']])
    #     urgency_percentage = round((critical_high / total_tasks * 100), 2) if total_tasks > 0 else 0
        
    #     # Stability index
    #     stability = task_service.get_stability_index()
        
    #     # Today's mission
    #     todays_mission = task_service.get_todays_mission()
        
    #     # Get last backup time
    #     last_backup = get_last_backup_time()
        
    #     # Get task counts for sections
    #     today_count = len(task_service.get_tasks_due_today())
    #     overdue_count = len(task_service.get_overdue_tasks())
    #     upcoming_count = len(task_service.get_upcoming_tasks(days=7))
        
    #     return render_template('index.html', 
    #                          tasks=tasks,
    #                          suggestions=suggestions,
    #                          completion_percentage=completion_percentage,
    #                          urgency_percentage=urgency_percentage,
    #                          stability=stability,
    #                          todays_mission=todays_mission,
    #                          current_filter=filter_type,
    #                          show_archived=show_archived,
    #                          last_backup=last_backup,
    #                          today_count=today_count,
    #                          overdue_count=overdue_count,
    #                          upcoming_count=upcoming_count,
    #                          task_service=task_service)
    
    @app.route('/')
    def index():
        filter_type = request.args.get('filter', 'all')
        show_archived = request.args.get('archived', 'false') == 'true'
        
        # Get tasks with archive filter
        if show_archived:
            tasks = task_service.get_archived_tasks()
        else:
            tasks = task_service.get_filtered_tasks(filter_type)
        
        # Get suggestions for today
        suggestions = task_service.get_suggestions()
        
        # Calculate stats
        all_tasks = task_service.get_all(include_archived=False)
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t.completed])
        completion_percentage = round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0
        critical_high = len([t for t in all_tasks if not t.completed and t.priority in ['Critical', 'High']])
        urgency_percentage = round((critical_high / total_tasks * 100), 2) if total_tasks > 0 else 0
        
        # Stability index
        stability = task_service.get_stability_index()
        
        # Today's mission
        todays_mission = task_service.get_todays_mission()
        
        # Get last backup time
        from services.backup_service import get_last_backup_time
        last_backup = get_last_backup_time()
        last_backup_formatted = last_backup.strftime('%B %d, %I:%M %p') if last_backup else None
        
        return render_template('index.html', 
                            tasks=tasks,
                            suggestions=suggestions,
                            completion_percentage=completion_percentage,
                            urgency_percentage=urgency_percentage,
                            stability=stability,
                            todays_mission=todays_mission,
                            current_filter=filter_type,
                            show_archived=show_archived,
                            last_backup_time=last_backup_formatted,
                            completed_tasks=completed_tasks,
                            total_tasks=total_tasks,
                            critical_high=critical_high,
                            task_service=task_service)
        
    
    @app.route('/add', methods=['POST'])
    def add_task():
        title = request.form.get('title')
        priority = request.form.get('priority', 'Medium')
        due_date = request.form.get('due_date')
        domain = request.form.get('domain', 'General')
        repeat = request.form.get('repeat') or None
        
        if title:
            try:
                task_service.add_task(title, priority, due_date, domain, repeat)
                print(f"✅ Task added: {title} (repeat: {repeat})")
            except Exception as e:
                print(f"❌ Error adding task: {e}")
        
        return redirect(url_for('index'))
    
    @app.route('/toggle/<int:task_id>')
    def toggle_task(task_id):
        try:
            task_service.toggle(task_id)
            print(f"✅ Task {task_id} toggled")
        except Exception as e:
            print(f"❌ Error toggling task: {e}")
        return redirect(url_for('index'))
    
    @app.route('/delete/<int:task_id>')
    def delete_task(task_id):
        try:
            task_service.soft_delete(task_id)  # Now uses soft delete
            print(f"✅ Task {task_id} archived")
        except Exception as e:
            print(f"❌ Error archiving task: {e}")
        return redirect(url_for('index'))
    
    @app.route('/restore/<int:task_id>')
    def restore_task(task_id):
        try:
            task_service.restore(task_id)
            print(f"✅ Task {task_id} restored")
        except Exception as e:
            print(f"❌ Error restoring task: {e}")
        return redirect(url_for('index'))
    
    @app.route('/permanent-delete/<int:task_id>')
    def permanent_delete(task_id):
        try:
            task_service.permanent_delete(task_id)
            print(f"✅ Task {task_id} permanently deleted")
        except Exception as e:
            print(f"❌ Error deleting task: {e}")
        return redirect(url_for('index'))
    
    @app.route('/check-reminders')
    def check_reminders():
        with app.app_context():
            try:
                check_due_tasks()
                print("✅ Reminders checked")
            except Exception as e:
                print(f"❌ Error checking reminders: {e}")
        return redirect(url_for('index'))
    
    @app.route('/api/tasks')
    def api_tasks():
        tasks = task_service.get_all(include_archived=False)
        return jsonify([{
            'id': t.id,
            'title': t.title,
            'priority': t.priority,
            'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None,
            'domain': t.domain,
            'completed': t.completed,
            'repeat': t.repeat,
            'next_occurrence': task_service.get_next_occurrence(t) if t.repeat and not t.completed else None
        } for t in tasks])
    
    @app.route('/backup')
    def backup_tasks():
        """Generate and download a CSV backup of all tasks"""
        try:
            filename = backup_tasks_to_csv()
            download_filename = f"tasks_backup_{datetime.now().strftime('%Y-%m-%d')}.csv"
            
            return send_file(
                filename, 
                as_attachment=True, 
                download_name=download_filename,
                mimetype='text/csv'
            )
        except Exception as e:
            return f"❌ Backup failed: {e}"
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for Render - FIXED with text()"""
        try:
            with app.app_context():
                # FIXED: Use text() for raw SQL in SQLAlchemy 2.0
                db.session.execute(text('SELECT 1')).scalar()
            return jsonify({"status": "healthy", "database": "connected"}), 200
        except Exception as e:
            return jsonify({"status": "unhealthy", "error": str(e)}), 500
    
    return app

# Create the application instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)