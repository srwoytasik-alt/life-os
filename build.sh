#!/usr/bin/env bash
# Install system dependencies for psycopg2
apt-get update && apt-get install -y libpq-dev gcc

# Install Python dependencies
pip install -r requirements.txt
