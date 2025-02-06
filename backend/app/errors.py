import logging
from enum import Enum
from fastapi import HTTPException, status

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class ErrorCode(Enum):
    GENERIC_ERROR = (1, "A generic error occurred")
    DATABASE_ERROR = (2, "A database error occurred")
    INVALID_INPUT = (3, "Invalid input provided")
    NOT_FOUND = (404, "Data not found")
    UNAUTHORIZED = (401, "Unauthorized access")
    FORBIDDEN = (403, "Access forbidden")
    SERVER_ERROR = (500, "Internal server error")

    def __init__(self, code, message):
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
            status_code=self.code if self.code != 500 else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=self.message,
        )

def fetch_example_data(data):
    if not data:
        ErrorCode.NOT_FOUND.raise_exception()
    return data