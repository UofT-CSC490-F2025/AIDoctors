from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors (422).
    Provides more user-friendly error messages.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        msg = error["msg"]
        error_type = error["type"]
        
        # Customize message based on error type
        if error_type == "missing":
            custom_msg = f"Required field '{field}' is missing"
        elif error_type == "value_error":
            custom_msg = f"Invalid value for field '{field}': {msg}"
        elif error_type == "type_error":
            custom_msg = f"Field '{field}' has incorrect type: {msg}"
        else:
            custom_msg = f"Validation error in field '{field}': {msg}"
        
        errors.append({
            "field": field,
            "message": custom_msg,
            "type": error_type
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )
