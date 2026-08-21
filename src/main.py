"""
main.py
-------
Runs the full end-to-end demo pipeline:

  LIVE TELEMETRY -> SENTINEL (detect, diagnose, forecast)
                  -> ORBITAL MEMORY (search historical events)
                  -> SYNTHESIS (combined, evidence-grounded risk card)

This is the file to run for your demo video. It prints a full risk card
to the terminal. Once this works, the natural next step is wrapping this
same logic in a simple web UI (e.g. Streamlit) -- but get this console
version working first and reliably before adding a UI layer.

Run it with:  python src/main.py
"""

from telemetry_simulator import generate_demo_stream
from sentinel import run_sentinel
from orbital_memory import find_similar_events
from synthesis import build_risk_card, print_risk_card


def run_demo():
    print("Generating simulated telemetry stream (60 minutes: 30 normal + 30 anomalous)...\n")
    readings = generate_demo_stream()

    print("Running SENTINEL (detect -> diagnose -> forecast)...\n")
    sentinel_result = run_sentinel(readings)

    diagnosis = sentinel_result["diagnosis"]
    if not diagnosis["anomaly_detected"]:
        print("No anomaly detected in this run. (Telemetry is randomized -- try running again,")
        print("or check telemetry_simulator.py's drift rates if this happens consistently.)")
        return

    print("Searching ORBITAL MEMORY for similar historical events...\n")
    matches = find_similar_events(diagnosis["flagged_signals"])

    print("Synthesizing combined risk card...\n")
    card = build_risk_card(sentinel_result, matches)

    print_risk_card(card)


if __name__ == "__main__":
    run_demo()
