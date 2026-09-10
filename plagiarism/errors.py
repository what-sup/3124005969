"""Domain-specific errors for the plagiarism checker."""


class PlagiarismError(Exception):
    """Base class for expected application errors."""


class InputFileError(PlagiarismError):
    """Raised when an input file cannot be read."""


class TextDecodeError(InputFileError):
    """Raised when an input file cannot be decoded as supported text."""


class OutputFileError(PlagiarismError):
    """Raised when the answer file cannot be written."""


class InvalidArgumentsError(PlagiarismError):
    """Raised when the command-line argument contract is invalid."""
