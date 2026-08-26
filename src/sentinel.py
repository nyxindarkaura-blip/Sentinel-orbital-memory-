"""
sentinel.py
-----------
SENTINEL answers: "What is happening to the spacecraft right now?"

It takes a stream of telemetry readings and does three things, in order:
 1. DETECT   -- is there an anomaly, and how severe is it?
 2. DIAGNOSE -- which signals are driving it, and by how much?
 3. FORECAST -- if the current trend continues, where does this go?

This is deliberately built with simple, explainable statistics (rolling
baselines and percentage change) rather than a black-box model. For a
13-day beginner-friendly prototype, "simple and correct" beats "complex
and mysterious" -- and it's much easier to explain in your demo video.
"""

from statistics import mean

from errors import InvalidTelemetryError


NORMAL_BASELINE_MINUTES = 30  # how many early readings we treat as "normal" to compare against
REQUIRED_FIELDS = ("minute", "battery_voltage", "current", "temperature")


def _validate_readings(readings, minimum_length=1):
    """
    Validates a list of telemetry readings before any analysis runs.

    Checks, in order:
     - readings is a non-empty list
     - there are enough readings to analyze (minimum_length)
     - every reading is a dict with all required fields
     - every required field is a real number (not a string, None, NaN, etc.)

    Raises InvalidTelemetryError with a specific, human-readable message
    on the first problem found, rather than letting the pipeline fail
    later with a confusing KeyError or TypeError.
    """
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
                )

            value = reading[field]
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise InvalidTelemetryError(
                    f"Reading at index {i}, field '{field}' must be a number, "
                    f"got {type(value).__name__} ({value!r})."
                )
            if isinstance(value, float) and (value != value):  # NaN check (NaN != NaN)
                raise InvalidTelemetryError(
                    f"Reading at index {i}, field '{field}' is NaN, which is not a valid telemetry value."
                )


def _baseline(readings):
    """Compute the average of each signal over the first N readings (the 'normal' window)."""
    window = readings[:NORMAL_BASELINE_MINUTES]
    baseline = {
        "battery_voltage": mean(r["battery_voltage"] for r in window),
        "current": mean(r["current"] for r in window),
        "temperature": mean(r["temperature"] for r in window),
    }
    for signal, value in baseline.items():
        if value == 0:
            raise InvalidTelemetryError(
                f"Baseline for '{signal}' is 0, which would cause a divide-by-zero error "
                f"when computing percent change. Check the input telemetry."
            )
    return baseline


def _percent_change(baseline_value, current_value):
    return round(((current_value - baseline_value) / baseline_value) * 100, 1)


def detect_and_diagnose(readings, threshold_percent: float = 5.0):
    """
    DETECT + DIAGNOSE.

    Compares the most recent reading against the established baseline.
    If enough signals have drifted past `threshold_percent`, it's flagged
    as an anomaly, and we record which signals changed and by how much.

    Returns a dict describing the current state -- this is SENTINEL's
    "WHAT happened" and "WHY is it happening" answer.

    Raises InvalidTelemetryError if `readings` is malformed (see
    _validate_readings) or if `threshold_percent` is not a positive number.
    """
    _validate_readings(readings, minimum_length=1)

    if not isinstance(threshold_percent, (int, float)) or isinstance(threshold_percent, bool) or threshold_percent <= 0:
        raise InvalidTelemetryError(
            f"threshold_percent must be a positive number, got {threshold_percent!r}."
        )

    baseline = _baseline(readings)
    latest = readings[-1]

    changes = {
        "battery_voltage": _percent_change(baseline["battery_voltage"], latest["battery_voltage"]),
        "current": _percent_change(baseline["current"], latest["current"]),
        "temperature": _percent_change(baseline["temperature"], latest["temperature"]),
    }

    # Which signals moved past the threshold, in an "unhealthy" direction?
    # (voltage dropping is bad; current and temperature rising are bad)
    flags = []
    if changes["battery_voltage"] <= -threshold_percent:
        flags.append(("battery_voltage", changes["battery_voltage"]))
    if changes["current"] >= threshold_percent:
        flags.append(("current", changes["current"]))
    if changes["temperature"] >= threshold_percent:
        flags.append(("temperature", changes["temperature"]))

    anomaly_detected = len(flags) >= 2  # require at least 2 correlated signals, like the real MGS pattern

    # Simple confidence score: more flagged signals + bigger deviations = higher confidence
    magnitude = 0
    if anomaly_detected:
        magnitude = sum(abs(v) for _, v in flags)
        confidence = min(95, round(50 + magnitude * 2))
    else:
        confidence = 0

    severity = "Low"
    if anomaly_detected:
        if magnitude >= 25:
            severity = "High"
        elif magnitude >= 12:
            severity = "Medium"
        else:
            severity = "Low"

    return {
        "baseline": baseline,
        "latest_reading": latest,
        "changes_percent": changes,
        "flagged_signals": flags,
        "anomaly_detected": anomaly_detected,
        "severity": severity,
        "confidence": confidence,
    }


def forecast_trajectory(readings, lookback_minutes: int = 15):
    """
    FORECAST.

    Looks at the trend over the last `lookback_minutes` of readings and
    linearly extrapolates: "if this rate of change continues, where will
    voltage/current/temperature be in 30 and 60 minutes?"

    This is intentionally a simple trend extrapolation, not a trained
    predictive model -- fully explainable, and honest about being simple,
    which is a strength for a prototype: it's fast to build, easy to trust,
    and easy to explain in a demo video.

    Raises InvalidTelemetryError if `readings` is malformed or shorter
    than `lookback_minutes`, or if `lookback_minutes` is not a positive
    integer.
    """
    if not isinstance(lookback_minutes, int) or isinstance(lookback_minutes, bool) or lookback_minutes <= 0:
        raise InvalidTelemetryError(
            f"lookback_minutes must be a positive integer, got {lookback_minutes!r}."
        )

    _validate_readings(readings, minimum_length=lookback_minutes)

    recent = readings[-lookback_minutes:]
    first, last = recent[0], recent[-1]
    elapsed = last["minute"] - first["minute"]
    if elapsed == 0:
        elapsed = 1

    rates = {
        "battery_voltage": (last["battery_voltage"] - first["battery_voltage"]) / elapsed,
        "current": (last["current"] - first["current"]) / elapsed,
        "temperature": (last["temperature"] - first["temperature"]) / elapsed,
    }

    def project(signal, minutes_ahead):
        return round(last[signal] + rates[signal] * minutes_ahead, 2)

    forecast = {}
    for horizon in (30, 60):
        forecast[horizon] = {
            "battery_voltage": project("battery_voltage", horizon),
            "current": project("current", horizon),
            "temperature": project("temperature", horizon),
        }

    # Trend label used in the risk card
    trend = "Worsening" if rates["temperature"] > 0 and rates["battery_voltage"] < 0 else "Stable"

    return {
        "rates_per_minute": rates,
        "trend": trend,
        "forecast": forecast,
    }


def run_sentinel(readings):
    """
    Runs the full SENTINEL pipeline: detect + diagnose + forecast.

    Raises InvalidTelemetryError if `readings` is malformed or too short
    for the forecasting step (needs at least 15 readings by default).
    """
    diagnosis = detect_and_diagnose(readings)
    projection = forecast_trajectory(readings)
    return {
        "diagnosis": diagnosis,
        "forecast": projection,
    }


if __name__ == "__main__":
    from telemetry_simulator import generate_demo_stream

    stream = generate_demo_stream()

    try:
        result = run_sentinel(stream)
    except InvalidTelemetryError as e:
        print(f"SENTINEL could not process the telemetry stream: {e}")
    else:
        print("=== SENTINEL: Detection & Diagnosis ===")
        print("Anomaly detected:", result["diagnosis"]["anomaly_detected"])
        print("Severity:", result["diagnosis"]["severity"])
        print("Confidence:", f"{result['diagnosis']['confidence']}%")
        print("Flagged signals:", result["diagnosis"]["flagged_signals"])
        print()
        print("=== SENTINEL: Forecast ===")
        print("Trend:", result["forecast"]["trend"])
        print("Projected in 30 min:", result["forecast"]["forecast"][30])
        print("Projected in 60 min:", result["forecast"]["forecast"][60])

