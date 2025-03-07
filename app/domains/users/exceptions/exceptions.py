from fastapi import HTTPException, status

class UserAlreadyExistsError(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username '{username}' already exists",
            headers={"X-Error": "User Already Exists"}
        )

class InvalidCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

class UserNotFoundError(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username '{username}' not found",
            headers={"X-Error": "User Not Found"}
        ) 