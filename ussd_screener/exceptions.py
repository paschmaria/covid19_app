# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass

class UnexpectedMessageError(Error):
    """Exception for when user types and unexpected message"""
    pass