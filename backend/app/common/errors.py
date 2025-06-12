import logging
from enum import Enum
from fastapi import HTTPException, status

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class ErrorCode(Enum):
    GENERIC_ERROR = (1000, "A generic error occurred")
    DATABASE_ERROR = (1001, "A database error occurred")
    INVALID_INPUT = (1002, "Invalid input provided")
    NOT_FOUND = (404, "Data not found")
    UNAUTHORIZED = (401, "Invalid credentials")
    FORBIDDEN = (403, "Access forbidden")
    SERVER_ERROR = (500, "Internal server error")
    REDIS_ERROR = (1003, "Redis connection error")

    def __init__(self, code: int, message: str):
        self._code = code
        self._message = message

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    def raise_exception(self):
        logger.error(f"Exception raised: {self.code} - {self.message}")
        raise HTTPException(
            status_code=self.code if 400 <= self.code <= 599 else 500,  # keep it valid HTTP
            detail={"error_code": self.code, "error_message": self.message}
        )
