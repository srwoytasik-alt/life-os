# # wsgi.py

# from app import create_app

# # This creates the application instance that Gunicorn will use
# app = create_app()

# if __name__ == "__main__":
#     app.run()

# Create wsgi.py in your project root
cat > wsgi.py << 'EOF'
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
EOF