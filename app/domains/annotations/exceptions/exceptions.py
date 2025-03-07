from fastapi import HTTPException, status

class AnnotationNotFoundError(HTTPException):
    def __init__(self, annotation_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Annotation with ID {annotation_id} not found",
            headers={"X-Error": "Annotation Not Found"}
        )

class InvalidAnnotationPositionError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid annotation positions",
            headers={"X-Error": "Invalid Annotation Position"}
        ) 