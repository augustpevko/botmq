from .base import Base 

class Context:
    """
    Context manager for handling database operations.

    Attributes:
        handler (Base): An instance of a class that inherits from the Base abstract class,
                        responsible for database operations.
    """

    def __init__(self, handler: Base):
        """
        Initialize the Context manager with a database handler.

        Args:
            handler (Base): An instance of a class that implements the Base abstract class.
        """
        self.handler = handler
        self.handler.connect()

    def __enter__(self):
        """
        Enter the runtime context related to this object.

        The `connect` method of the handler is called to ensure the database connection is opened.

        Returns:
            Context: The instance of the context manager.
        """
        self.handler.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context related to this object.

        The `close` method of the handler is called to ensure the database connection is closed.

        Args:
            exc_type (type): The exception type, if any.
            exc_value (Exception): The exception instance, if any.
            traceback (TracebackType): The traceback object, if any.
        """
        self.handler.close()

    def __getattr__(self, attr):
        """
        Delegate attribute access to the handler.

        If the attribute is not found in the Context class, it is looked up in the handler.

        Args:
            attr (str): The name of the attribute.

        Returns:
            Any: The attribute value from the handler if it exists.

        Raises:
            AttributeError: If the attribute is not found in the handler.
        """
        if hasattr(self.handler, attr):
            return getattr(self.handler, attr)
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attr}'")
