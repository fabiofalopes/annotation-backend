import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_URL", "http://annotation_api:8000")
ADMIN_API_URL = f"{API_BASE_URL}/admin-api"

# UI Configuration
PAGE_TITLE = "Admin Dashboard"
PAGE_ICON = "📊"

# Animation URLs
LOADING_ANIMATION_URL = "https://assets5.lottiefiles.com/packages/lf20_qm8eqzse.json"
SUCCESS_ANIMATION_URL = "https://assets2.lottiefiles.com/packages/lf20_s2lryxtd.json"

# Project Types (must match backend schema)
PROJECT_TYPES = ["chat_disentanglement", "text_classification", "other"]

# Container Types (must match backend schema)
CONTAINER_TYPES = ["chat_rooms", "documents"] 