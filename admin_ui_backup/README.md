# Annotation Backend Admin UI

A Streamlit-based admin interface for the Annotation Backend API. This UI allows admins to:

- Manage users and their permissions
- Create and manage annotation projects
- View and manage data containers
- Import data from CSV files

## Architecture

The Admin UI follows a simple, modular architecture:

```
admin_ui/
├── admin.py          # Core API client
├── main.py           # Entry point and navigation
├── views/            # UI view modules
│   ├── import_data.py
│   ├── projects.py  
│   ├── containers.py
│   ├── users.py
│   └── __init__.py
├── utils/            # Shared utilities
│   ├── ui_components.py
│   └── __init__.py
├── docker_entrypoint.sh
└── README.md
```

### Key Components

- **admin.py**: API client that communicates with the backend
- **main.py**: Entry point that handles authentication and navigation
- **views/**: Self-contained view modules for each section of the UI
- **utils/**: Reusable UI components and utility functions

## Development

### Prerequisites

- Python 3.9+
- Streamlit 1.10.0+
- Access to the Annotation Backend API

### Running Locally

1. Set up the environment:

```bash
# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/MacOS
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

2. Set the API URL environment variable:

```bash
export ANNO_API_URL="http://localhost:8000"  # Linux/MacOS
# or
set ANNO_API_URL=http://localhost:8000       # Windows
```

3. Run the Streamlit app:

```bash
cd admin_ui
streamlit run main.py
```

### Running with Docker

Use Docker Compose to run the entire system:

```bash
docker-compose up
```

## Adding New Features

### Adding a New Page

1. Create a new view file in the `views/` directory
2. Add the page to the navigation dictionary in `main.py`

### Adding UI Components

Common UI components should be added to `utils/ui_components.py` for reuse across views.

## Deployment

The Admin UI is designed to be deployed as a Docker container, typically alongside the Annotation Backend API. See `docker-compose.yml` for an example configuration. 