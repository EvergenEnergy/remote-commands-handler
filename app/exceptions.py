"""Exception classes for configuration-related errors."""


class ConfigurationFileNotFoundError(Exception):
    """Exception raised when the configuration file is not found."""

    def __init__(self, path, message="Configuration file not found: "):
        self.path = path
        self.message = message + path
        super().__init__(self.message)


class ConfigurationFileInvalidError(Exception):
    """Exception raised when the configuration file contains errors."""

    def __init__(self, message="Configuration file contains errors"):
        super().__init__(message)


class InvalidArgumentError(Exception):
    """Exception raised when a function is called with invalid arguments."""

    def __init__(self, message="Unknown argument"):
        super().__init__(message)
