# Annotation Backend Admin UI

A Streamlit-based admin interface for managing the Annotation Backend.

## Structure

The admin UI is organized into a simple, flat structure:

```
admin_ui/
  ├── main.py              # Main Streamlit app entry point
  ├── admin.py             # Admin backend client
  ├── pages/              
  │   ├── users.py         # User management page
  │   ├── projects.py      # Project management page
  │   ├── containers.py    # Container management page
  │   └── import_data.py   # Data import page
  ├── components/
  │   ├── auth.py          # Authentication components
  │   ├── navigation.py    # Navigation sidebar
  │   └── data_display.py  # Reusable data display components
  └── README.md            # This file
```

## Philosophy

This UI follows a simple, monolithic design philosophy:
- Minimal packaging and complexity
- Files are organized for clarity but kept as self-contained as possible
- Reusable components are extracted only when they provide clear value
- Focus on functionality over structure

## Running the UI

To run the admin UI:

```bash
streamlit run admin_ui/main.py
```

## Development

When adding new features:
1. If it's page-specific, add it to the relevant page file
2. If it's truly reusable, add it to components
3. Keep files self-contained when possible
4. Avoid creating new directories or complex structures 