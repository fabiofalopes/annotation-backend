#!/bin/bash

# Wait for the API to be ready
echo "Waiting for API to be ready..."
while ! curl -s http://annotation_api:8000/health > /dev/null; do
    sleep 1
done
echo "API is ready!"

# Start the Streamlit app
exec streamlit run admin_ui/main.py --server.address 0.0.0.0 --server.port 8501 