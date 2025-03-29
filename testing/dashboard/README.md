# Project Dashboard Test Implementation

This is a test implementation of the project management dashboard using Streamlit. It demonstrates the core functionality before integration into the main admin UI.

## Setup

1. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
.\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
   - Copy `.env.example` to `.env`
   - Update `API_BASE_URL` if your FastAPI backend is running on a different port

## Running the Test

1. Make sure your FastAPI backend is running
2. Start the Streamlit app:
```bash
streamlit run test_projects.py
```

## Features

- **Authentication**
  - Login/logout functionality
  - Token-based authentication
  - Session management

- **Project Management**
  - List all projects in a sortable grid
  - Create new projects
  - View project details
  - Delete projects (with confirmation)

- **UI Components**
  - Modern sidebar navigation
  - Data tables with sorting and filtering
  - Custom notifications
  - Loading animations
  - Responsive layout

## Troubleshooting

1. **Installation Issues**
   - If you get version conflicts, try: `pip install -r requirements.txt --no-cache-dir`
   - For specific package issues, install them individually:
     ```bash
     pip install streamlit-option-menu
     pip install streamlit-aggrid
     pip install streamlit-lottie
     pip install streamlit-custom-notification-box==0.1.2
     ```

2. **API Connection Issues**
   - Verify FastAPI backend is running
   - Check `API_BASE_URL` in `.env` file
   - Ensure you have an admin user created in the backend

3. **UI Issues**
   - Clear browser cache
   - Try running `streamlit clear_cache`
   - Restart the Streamlit server

## Next Steps

After testing this implementation:
1. Review UI/UX flow
2. Test all API interactions
3. Plan integration into main admin UI
4. Add additional features:
   - Project statistics
   - User management
   - Activity logs
   - Advanced filtering 