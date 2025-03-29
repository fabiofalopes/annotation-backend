# Admin Dashboard

A Streamlit-based admin dashboard for managing projects, users, and data containers.

## Features

- 🔐 Secure authentication
- 📁 Project management
  - Create and list projects
  - Project details and statistics
  - User assignment
  - Container management
- 👥 User management (coming soon)
- ⚙️ Settings configuration

## Directory Structure

```
admin_ui/
├── src/
│   ├── api/            # API client and endpoints
│   ├── components/     # Reusable UI components
│   ├── config/         # Configuration and settings
│   ├── pages/          # Page components
│   └── utils/          # Utility functions
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the `admin_ui` directory:
   ```
   API_BASE_URL=http://localhost:8000
   ```

## Running the Dashboard

1. Make sure the FastAPI backend is running
2. From the `admin_ui` directory, run:
   ```bash
   streamlit run src/app.py
   ```

## Development

### Adding New Features

1. Create new API endpoints in `src/api/`
2. Add new pages in `src/pages/`
3. Create reusable components in `src/components/`
4. Update configuration in `src/config/`

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions and classes
- Keep components focused and reusable

### Testing

- Test new features in isolation
- Verify API integration
- Check error handling
- Test responsiveness

## Next Steps

- [ ] Implement user management
- [ ] Add role-based access control
- [ ] Enhance project statistics
- [ ] Add data visualization
- [ ] Implement activity logging 