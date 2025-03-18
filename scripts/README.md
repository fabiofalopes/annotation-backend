# Admin Script for Annotation Backend

## Overview

The `admin.py` script provides a comprehensive command-line interface for managing the Annotation Backend. It interacts with the FastAPI API endpoints to perform administrative tasks including:

- **User Management**: Create, list, view, and delete users
- **Project Management**: Create, list, view, and delete projects
- **Data Container Management**: Create, list, and view data containers
- **Data Import**: Import chat room data from CSV files

## Requirements

The script requires the following Python packages:
- requests
- pandas
- tabulate
- argparse (standard library)

You can install them using:
```
pip install -r requirements.txt
```

## Configuration

The script can be configured using either command-line arguments or environment variables:

- API URL: Can be set using the `--url` argument or the `ANNO_API_URL` environment variable (default: `http://localhost:8000`)
- Authentication Token: Can be set using the `--token` argument or the `ANNO_API_TOKEN` environment variable

## Authentication

Before using most commands, you need to authenticate. Use the login command:

```
./admin.py login username password
```

This will provide an authentication token that will be used for subsequent requests. The token will be printed to the console, and you can save it as an environment variable for future use:

```
export ANNO_API_TOKEN="your-token-here"
```

## Common Usage Examples

### User Management

List all users:
```
./admin.py users list
```

Create a new user:
```
./admin.py users create username user@example.com password --role annotator
```

**Note**: Passwords must be at least 8 characters long.

Get details of a specific user:
```
./admin.py users get 1
```

Delete a user:
```
./admin.py users delete 1
```

### Project Management

List all projects:
```
./admin.py projects list
```

Create a new project:
```
./admin.py projects create "Project Name" chat_disentanglement --description "Project Description"
```

Get details of a specific project:
```
./admin.py projects get 1
```

Add a user to a project:
```
./admin.py projects add-user 1 2  # Add user with ID 2 to project with ID 1
```

Remove a user from a project:
```
./admin.py projects remove-user 1 2  # Remove user with ID 2 from project with ID 1
```

### Data Container Management

List all data containers:
```
./admin.py containers list
```

List data containers for a specific project:
```
./admin.py containers list --project-id 1
```

Create a new data container:
```
./admin.py containers create "Container Name" chat_room 1
```

### Data Import

Import a chat room from a CSV file:
```
./admin.py import chat-room 1 path/to/chatroom.csv --name "Chat Room Name"
```

The CSV file should have the following columns:
- `turn_id`: Unique identifier for the message
- `user_id`: Identifier for the user who sent the message
- `content`: The message content
- `reply_to`: The turn_id of the message this message is replying to

## Full Command Reference

For a full list of commands and options, run:
```
./admin.py --help
```

For help with a specific command, run:
```
./admin.py COMMAND --help
```

For help with a specific subcommand, run:
```
./admin.py COMMAND SUBCOMMAND --help
``` 