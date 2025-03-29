#!/bin/bash
set -e

# Wait for the API to be ready
echo "Waiting for API to be ready..."
until curl -f http://annotation_api:8000/docs > /dev/null 2>&1; do
    echo "API is unavailable - sleeping"
    sleep 2
done

echo "API is up - starting admin UI"

# Start Streamlit
cd /app/admin_ui/src
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0 