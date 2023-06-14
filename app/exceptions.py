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


class InvalidMessageError(Exception):
    """Exception raised when a message is not in the required format."""

    def __init__(self, message):
        super().__init__(message)


class ModbusClientError(Exception):
    """Exception raised when we fail to connect to the Modbus server."""

    def __init__(self, message):
        super().__init__(message)


class UnknownCommandError(Exception):
    """Exception raised when no coil or register is found matching the specified message action."""

    def __init__(self, action):
        super().__init__(f"No coil or register found to match {action!r}")
