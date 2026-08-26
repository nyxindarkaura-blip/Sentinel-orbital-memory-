"""
telemetry_simulator.py
-----------------------
Generates a simulated stream of spacecraft telemetry for the demo scenario:
a power/thermal degradation pattern modeled on the real Mars Global Surveyor
(2006) incident -- battery voltage declining, current increasing, and
temperature rising over time.

This is intentionally simple and readable: a beginner should be able to
follow every line. It produces a list of "readings", each a dictionary with
a timestamp (in minutes from the start) and the telemetry values at that
moment.

Why simulate instead of using a huge real dataset? For a 13-day prototype,
a small, well-understood, clearly-labeled simulation is easier to explain,
easier to debug, and easier to demo than wrangling a large real dataset --
and it still proves the AI pipeline works. You can swap this out for a real
dataset later (e.g. the NASA space weather dataset from the optional
GitHub Learning Lab) without changing anything downstream.
"""

import random


def generate_normal_telemetry(minutes: int = 30, start_minute: int = 0):
    """Generate telemetry that looks healthy / within normal range."""
    readings = []
    for m in range(start_minute, start_minute + minutes):
        readings.append({
            "minute": m,
            "battery_voltage": round(28.4 + random.uniform(-0.1, 0.1), 2),  # volts
            "current": round(4.8 + random.uniform(-0.1, 0.1), 2),           # amps
            "temperature": round(31.0 + random.uniform(-0.3, 0.3), 2),      # celsius
        })
    return readings


def generate_anomaly_telemetry(minutes: int = 30, start_minute: int = 30):
    """
    Generate telemetry that drifts the way MGS's did before its 2006 loss:
    voltage slowly declining, current slowly rising, temperature slowly
    rising -- individually small changes, but together an abnormal pattern.
    """
    readings = []
    voltage = 28.4
    current = 4.8
    temperature = 31.0

    for i, m in enumerate(range(start_minute, start_minute + minutes)):
        # Small persistent drift each minute, plus a little noise
        voltage -= random.uniform(0.02, 0.05)
        current += random.uniform(0.02, 0.05)
        temperature += random.uniform(0.08, 0.15)

        readings.append({
            "minute": m,
            "battery_voltage": round(voltage, 2),
            "current": round(current, 2),
            "temperature": round(temperature, 2),
        })
    return readings


def generate_demo_stream():
    """
    Full demo telemetry stream: 30 minutes normal, then 30 minutes of the
    MGS-style anomaly pattern. This is what main.py feeds into SENTINEL.
    """
    normal = generate_normal_telemetry(minutes=30, start_minute=0)
    anomaly = generate_anomaly_telemetry(minutes=30, start_minute=30)
    return normal + anomaly


if __name__ == "__main__":
    # Quick manual check: run this file directly to see sample output.
    stream = generate_demo_stream()
    print(f"Generated {len(stream)} telemetry readings.")
    print("First reading:", stream[0])
    print("Last reading:", stream[-1])
