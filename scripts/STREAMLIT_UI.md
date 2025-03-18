# Streamlit Admin UI for Annotation Backend

## Overview

The `streamlit_admin_ui.py` script provides a lightweight, Python-based web UI for managing the Annotation Backend. This UI is built using Streamlit and serves as a frontend for the same functionality provided by the admin.py command-line script.

> **Note**: This is a future consideration (Stage 2) and is provided as a proof of concept to demonstrate how the admin script can be integrated into a web-based UI.

## Features

The UI provides interfaces for:
- **User Management**: Create, list, view, and delete users
- **Project Management**: Create, list, view, and delete projects; manage project users
- **Data Container Management**: Create, list, and view data containers
- **Data Import**: Import chat room data from CSV files with column mapping

## Requirements

- Python 3.7+
- Streamlit
- All dependencies from the admin.py script

You can install them using:
```
pip install -r requirements.txt
```

## Running the UI

To launch the Streamlit UI, run:

```bash
# From the project root
streamlit run scripts/streamlit_admin_ui.py

# Or directly 
./scripts/streamlit_admin_ui.py
```

The UI will be available at http://localhost:8501 by default.

## Authentication

The UI requires the same authentication as the API. On first launch, you will be prompted to:
1. Enter the API URL (defaults to http://localhost:8000)
2. Enter credentials (username and password)

The UI will then handle token-based authentication with the API.

## Future Development Considerations

This UI is intentionally kept minimal as a proof of concept. For a production-ready admin interface, consider the following enhancements:

1. **Persistent Authentication**: Store tokens securely to maintain sessions
2. **Improved Error Handling**: More robust error reporting and recovery
3. **Form Validation**: Client-side validation for all forms
4. **Bulk Operations**: Support for batch operations on multiple items
5. **Rich Filtering**: More advanced filtering and search options
6. **Pagination**: Better handling of large data sets
7. **Visualization**: Charts and graphs for usage statistics and activities
8. **Role-Based Access Control**: Different views and capabilities based on user roles
9. **Audit Logging**: Tracking of admin actions for security and compliance

## Integration with Admin Script

The Streamlit UI is designed to use the `AnnoBackendAdmin` class from the admin.py script directly. This integration demonstrates how the script can be leveraged beyond CLI usage, making it a versatile foundation for administrative interfaces.

The UI does not duplicate any business logic; it simply provides a web-based interface to the same functionality, maintaining the principle of keeping the system as simple as possible.

## Design Philosophy

The design adheres to the project's guiding principles:
1. **Simplicity**: Minimizing complexity while providing necessary functionality
2. **Leveraging Existing Functionality**: Building upon the admin script rather than duplicating logic
3. **Python-Based**: Using Python technologies to minimize the need for learning new technologies
4. **Modularity**: Clear separation of presentation and business logic

## Contributing

When enhancing this UI, please maintain the following guidelines:
1. Keep dependencies minimal
2. Maintain integration with the admin script
3. Prioritize simplicity and usability over advanced features
4. Document any new features or changes 