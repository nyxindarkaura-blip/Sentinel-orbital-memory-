"""
errors.py
---------
Custom exception types used across the pipeline (SENTINEL, ORBITAL MEMORY,
synthesis). Having named, specific exceptions -- instead of letting raw
KeyError/ZeroDivisionError/etc. bubble up -- makes failures easier to
catch, log, and explain to a user or in a demo, since each error message
says exactly what was wrong with the input and what was expected.
"""


class PipelineError(Exception):
    """Base class for all errors raised by this project's pipeline."""


class InvalidTelemetryError(PipelineError):
    """Raised when a telemetry reading (or list of readings) is malformed,
    e.g. missing required fields, wrong types, or too few readings to
    analyze."""


class InvalidHistoricalDataError(PipelineError):
    """Raised when the historical events dataset is missing, malformed,
    or an individual event record is missing required fields."""


class InvalidSignalError(PipelineError):
    """Raised when a flagged signal name isn't one of the pipeline's
    known telemetry signals."""
