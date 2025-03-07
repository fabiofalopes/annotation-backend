#!/bin/bash
set -e

# Create database tables if they don't exist
python -c "from app.infrastructure.database import create_tables; create_tables()"

# Run the command specified in CMD (uvicorn)
exec "$@" 