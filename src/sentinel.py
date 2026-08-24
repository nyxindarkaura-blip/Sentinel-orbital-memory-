""" sentinel.py ----------- SENTINEL answers: "What is happening to the spacecraft right now?" It takes a stream of telemetry readings and does three things, in order: 1. DETECT -- is there an anomaly, and how severe is it? 2. DIAGNOSE -- which signals are driving it, and by how much? 3. FORECAST -- if the current trend continues, where does this go? This is deliberately built with simple, explainable statistics (rolling baselines and percentage change) rather than a black-box model. For a 13-day beginner-friendly prototype, "simple and correct" beats "complex and mysterious" -- and it's much easier to explain in your demo video. """

from statistics import mean

from errors import InvalidTelemetryError


NORMAL_BASELINE_MINUTES = 30  # how many early readings we treat as "normal" to compare against
REQUIRED_FIELDS = ("minute", "battery_voltage", "current", "temperature")


def _validate_readings(readings, minimum_length=1):
    """ Validates a list of telemetry readings before any analysis runs. Checks, in order: - readings is a non-empty list - there are enough readings to analyze (minimum_length) - every reading is a dict with all required fields - every required field is a real number (not a string, None, NaN, etc.) Raises InvalidTelemetryError with a specific, human-readable message on the first problem found, rather than letting the pipeline fail later with a confusing KeyError or TypeError. """
    if readings is None:
        raise InvalidTelemetryError("Telemetry readings is None -- expected a list of reading dicts.")

    if not isinstance(readings, list):
        raise InvalidTelemetryError(f"Telemetry readings must be a list, got {type(readings).__name__}.")

    if len(readings) == 0:
        raise InvalidTelemetryError("Telemetry readings list is empty -- at least one reading is required.")

    if len(readings) < minimum_length:
        raise InvalidTelemetryError(
            f"Not enough telemetry readings to analyze: got {len(readings)}, "
            f"need at least {minimum_length}."
        )

    for i, reading in enumerate(readings):
        if not isinstance(reading, dict):
            raise InvalidTelemetryError(
                f"Reading at index {i} is not a dict (got {type(reading).__name__})."
            )

        for field in REQUIRED_FIELDS:
            if field not in reading:
                raise InvalidTelemetryError(
                    f"Reading at index {i} is missing required field '{field}'. "
                    f"Expected fields: {REQUIRED_FIELDS}."
