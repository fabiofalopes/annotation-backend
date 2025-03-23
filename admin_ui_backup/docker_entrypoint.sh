#!/bin/bash
set -e

# Wait for the API to be ready
echo "Waiting for API to be ready..."
until curl -f http://annotation_api:8000/docs > /dev/null 2>&1; do
    echo "API is unavailable - sleeping"
    sleep 2
done
echo "API is up - starting admin UI"

# Run the command specified in CMD (streamlit)
exec "$@" 