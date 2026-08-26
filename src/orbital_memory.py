"""
orbital_memory.py
------------------
ORBITAL MEMORY answers: "Have we seen anything like this before, and what
did we learn from it?"

It holds a small, curated set of real, sourced historical spacecraft
incidents (see data/historical_events.json) and retrieves the ones most
relevant to what SENTINEL just detected.

Retrieval method: this uses simple, transparent keyword/signal overlap
scoring rather than a vector database. For a curated set of ~3-10 events,
this is honest, fast to build, fully explainable in a demo, and avoids
the "black box similarity score" problem -- you can show a judge exactly
why an event matched. It can be swapped for embeddings-based retrieval
later without changing anything else in the pipeline.
"""

import json
import os

from errors import InvalidHistoricalDataError, InvalidTelemetryError

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "historical_events.json")

# Maps SENTINEL's telemetry signal names to keywords likely to appear in
# a historical event's telemetry_pattern / summary text.
SIGNAL_KEYWORDS = {
    "battery_voltage": ["voltage", "battery"],
    "current": ["current", "power"],
    "temperature": ["temperature", "thermal", "heat", "overheat"],
}

REQUIRED_EVENT_FIELDS = ("id", "mission", "date", "summary", "root_cause", "outcome", "lesson", "source")


def load_events():
    """
    Loads and validates the curated historical events dataset.

    Raises InvalidHistoricalDataError if the file is missing, isn't valid
    JSON, isn't a list, or any individual event is missing required fields.
    This fails loudly and specifically rather than letting a malformed
    dataset silently produce blank or broken historical evidence later
    in the pipeline.
    """
    if not os.path.exists(DATA_PATH):
        raise InvalidHistoricalDataError(
            f"Historical events file not found at expected path: {DATA_PATH}"
        )

    with open(DATA_PATH, "r") as f:
        try:
            events = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidHistoricalDataError(
                f"Historical events file is not valid JSON: {e}"
            ) from e

    if not isinstance(events, list):
        raise InvalidHistoricalDataError(
            f"Historical events file must contain a JSON list, got {type(events).__name__}."
        )

    if len(events) == 0:
        raise InvalidHistoricalDataError(
            "Historical events file is empty -- at least one curated event is required."
        )

    for i, event in enumerate(events):
        if not isinstance(event, dict):
            raise InvalidHistoricalDataError(
                f"Historical event at index {i} is not a JSON object (got {type(event).__name__})."
            )
        for field in REQUIRED_EVENT_FIELDS:
            if field not in event or not event[field]:
                raise InvalidHistoricalDataError(
                    f"Historical event at index {i} (id={event.get('id', '?')}) is missing "
                    f"required field '{field}'."
                )

    return events


def _event_text(event):
    """Flatten the searchable text of an event into one lowercase string."""
    parts = [
        event.get("summary", ""),
        event.get("root_cause", ""),
        " ".join(event.get("telemetry_pattern", [])),
        event.get("subsystem", ""),
    ]
    return " ".join(parts).lower()


def score_event(event, flagged_signals):
    """
    Score one historical event against SENTINEL's flagged signals.

    flagged_signals is a list of (signal_name, percent_change) tuples,
    e.g. [("battery_voltage", -6.2), ("temperature", 9.1)]

    Score = how many of the flagged signal categories show up in the
    event's description, as a percentage of the flagged signals.
    """
    text = _event_text(event)
    matched = 0
    for signal_name, _ in flagged_signals:
        keywords = SIGNAL_KEYWORDS.get(signal_name, [])
        if any(kw in text for kw in keywords):
            matched += 1

    if not flagged_signals:
        return 0
    return round((matched / len(flagged_signals)) * 100)


def find_similar_events(flagged_signals, top_n: int = 3, min_score: int = 34):
    """
    Search the curated historical event set for events relevant to the
    signals SENTINEL flagged. Returns a list of (event, similarity_score)
    sorted by score descending, keeping only matches above min_score.

    Raises InvalidTelemetryError if `flagged_signals` isn't a list of
    (signal_name, value) pairs, or InvalidHistoricalDataError if the
    dataset itself is malformed (see load_events).
    """
    if not isinstance(flagged_signals, list):
        raise InvalidTelemetryError(
            f"flagged_signals must be a list of (signal_name, value) tuples, "
            f"got {type(flagged_signals).__name__}."
        )

    for i, item in enumerate(flagged_signals):
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise InvalidTelemetryError(
                f"flagged_signals[{i}] must be a 2-item (signal_name, value) pair, got {item!r}."
            )
        signal_name = item[0]
        if signal_name not in SIGNAL_KEYWORDS:
            raise InvalidTelemetryError(
                f"flagged_signals[{i}] has unknown signal name '{signal_name}'. "
                f"Expected one of: {list(SIGNAL_KEYWORDS.keys())}."
            )

    if not isinstance(top_n, int) or isinstance(top_n, bool) or top_n <= 0:
        raise InvalidTelemetryError(f"top_n must be a positive integer, got {top_n!r}.")

    events = load_events()
    scored = []
    for event in events:
        score = score_event(event, flagged_signals)
        if score >= min_score:
            scored.append((event, score))

    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_n]


if __name__ == "__main__":
    # Quick manual check using a sample flagged-signal set
    sample_flags = [("battery_voltage", -6.2), ("current", 8.4), ("temperature", 9.1)]
    try:
        matches = find_similar_events(sample_flags)
    except (InvalidTelemetryError, InvalidHistoricalDataError) as e:
        print(f"ORBITAL MEMORY could not complete the search: {e}")
    else:
        print(f"Found {len(matches)} similar historical event(s):\n")
        for event, score in matches:
            print(f"- {event['mission']} ({event['date']}) -- similarity: {score}%")
            print(f"  Outcome: {event['outcome']}")
            print()
