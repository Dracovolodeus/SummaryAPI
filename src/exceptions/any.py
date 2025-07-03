from logging import getLogger

logger = getLogger(__name__)


class BaseException(Exception):
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.text = message
        if message:
            logger.error(f"{self.__class__.__name__}: \"{message}\"")


class NotFoundError(BaseException): ...


class UnknownError(BaseException): ...

