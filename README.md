# SENTINEL + ORBITAL MEMORY

**IBM AI Builders Challenge — Theme: Space Exploration**

An AI system that watches live spacecraft telemetry, detects and diagnoses anomalies, forecasts where they're heading, and grounds its recommendation in real historical mission evidence — instead of just saying "anomaly detected" or "here are some old NASA reports."

---

## Problem Statement

Spacecraft continuously generate telemetry (voltage, current, temperature, attitude, and more). A small abnormality in any one signal can look harmless on its own, but a *combination* of small abnormalities can be an early warning sign of a serious failure. Mission operators face two hard problems at once:

1. **Detecting** a real anomaly early enough to act, without drowning in false alarms.
2. **Knowing what it means** — is this pattern actually dangerous, or is it noise? Has anything like this happened before, and how did it turn out?

A system that only answers "is something wrong?" isn't enough. Operators need to know **what's happening, why, what happens if it continues, and what to do about it** — and they need to trust that the recommendation isn't an AI guess, but grounded in real precedent.

## Solution Description

This project combines two subsystems into one pipeline:

- **SENTINEL** — monitors live telemetry and answers *"What is happening to the spacecraft right now?"* It detects anomalies, diagnoses which signals are driving them, and forecasts where the trend leads if nothing changes.
- **ORBITAL MEMORY** — a curated knowledge base of real, sourced historical spacecraft incidents. It answers *"Have we seen anything like this before, and what did we learn from it?"*

Neither one alone is enough. A live anomaly detector can tell you something looks wrong, but not whether it's actually dangerous. A historical lookup can tell you "something similar happened once," but has no idea what's happening on your spacecraft right now. **Combined**, they produce something neither can alone: a live risk assessment backed by cited historical evidence, e.g. *"This pattern resembles the Mars Global Surveyor (2006) power/thermal degradation, which led to total loss of the spacecraft — recommended action: review battery behavior and non-essential power loads."*

The combined output follows a four-part structure:

| Question | Answered by |
|---|---|
| **WHAT** happened? | SENTINEL — anomaly detection |
| **WHY** is it happening? | SENTINEL — root-cause / signal correlation |
| **WHAT IF** it continues? | SENTINEL — trend forecasting |
| **WHAT NOW**? | SYNTHESIS — evidence-grounded recommendation, citing ORBITAL MEMORY |

## AI Approach & Architecture

```
LIVE TELEMETRY
      |
      v
  SENTINEL
   - detect anomaly (compares current readings to an established baseline)
   - diagnose (identifies which signals are driving the anomaly, and by how much)
   - forecast (trend extrapolation: where do these signals go in 30/60 min?)
      |
      v
 ORBITAL MEMORY
   - searches a curated set of real historical mission incidents
   - scores each by relevance to the currently flagged signals
   - returns the most similar precedent(s), each with its real outcome and source
      |
      v
  SYNTHESIS
   - combines SENTINEL's live diagnosis + forecast with ORBITAL MEMORY's
     historical evidence into one risk card
   - every claim is either a computed number or a fact pulled directly
     from a sourced historical record — nothing is invented
```

**Why a curated historical dataset instead of ingesting "all of space history"?** A small (currently 3, expandable), well-documented, clearly-sourced set of real incidents is more reliable, more explainable, and far more achievable in the challenge timeline than a large uncurated document dump — and it directly avoids the hallucination risk that comes with an AI inventing a "lesson" a mission never actually had. See `data/historical_events.json` for the current curated set, each entry with real sources.

**Why simple statistics instead of a trained ML model for detection/forecasting?** For this prototype, transparent baseline-comparison and trend extrapolation are fully explainable (important for a decision-support tool judges and operators need to trust) and fast to build correctly. This is a clear, natural next step to extend with a trained model (e.g. Isolation Forest, LSTM) once the pipeline is proven.

## How IBM Bob Was Used

IBM Bob was used in two confirmed ways during development.
First, Bob was used to set up, run, and verify the project. The full codebase, including the backend pipeline and the web dashboard, was opened as a project folder inside Bob. The team used Bob's integrated terminal to run and test the application, confirming that the telemetry simulation, anomaly detection, historical evidence retrieval, and the live dashboard all worked correctly inside Bob's environment before anything was finalized.
Second, Bob was used to build the error handling connection between the backend and the dashboard. The team prompted Bob to wrap the simulation logic in the Flask API route in a try and except block, catching the project's custom PipelineError exceptions and returning a structured JSON error response with an HTTP 400 status code, instead of letting the server crash. Bob was also prompted to update the frontend JavaScript so that when the API returns an error, the exact error message is parsed from the response and shown to the user in a clear popup, rather than a generic failure message. This was tested directly by triggering a simulated error and confirming the correct message appeared on screen.
Bob served as the team's development and testing environment throughout the project, and specifically generated the error handling logic connecting the backend's validation system to the live dashboard.

## Selected Challenge Theme

**Space Exploration** — this directly addresses the challenge's call for AI that improves mission safety/reliability, turns space data from data-heavy into insight-driven, and supports better decision-making in complex, high-stakes environments.

## Project Structure

```
sentinel_orbital_memory/
├── README.md                    <- this file
├── requirements.txt             <- core pipeline dependencies (none required, uses standard library)
├── requirements-ui.txt          <- UI dashboard dependencies (Flask)
├── server.py                    <- Flask backend server serving UI and simulated data API
├── public/                      <- frontend Web UI dashboard static files
│   ├── index.html               <- main HTML structure
│   ├── style.css                <- dashboard styles
│   └── script.js                <- frontend telemetry visualization logic (Chart.js)
├── data/
│   └── historical_events.json   <- curated Mission Memory (Orbital Memory's dataset)
├── src/
│   ├── telemetry_simulator.py   <- generates the demo telemetry stream
│   ├── sentinel.py               <- detect, diagnose, forecast
│   ├── orbital_memory.py         <- historical event retrieval
│   ├── synthesis.py              <- combines both into the risk card
│   └── main.py                   <- run this for the end-to-end demo
└── docs/
    └── GETTING_STARTED.md        <- beginner-friendly setup + IBM Bob workflow guide
```

## Running the Demo

### Terminal Console Version
To run the terminal pipeline demo end-to-end:
```bash
cd src
python main.py
```
This runs the full pipeline end-to-end and prints a risk card to the terminal, modeled on the real Mars Global Surveyor (2006) incident.

### Web UI Dashboard Cockpit
To run the interactive web interface dashboard:
1. Install requirements:
   ```bash
   pip install -r requirements-ui.txt
   ```
2. Run the Flask server:
   ```bash
   python server.py
   ```
3. Open http://localhost:5000 in your web browser to view the real-time telemetry graphs, diagnostics engine, and historical correlation cards.

See [GETTING_STARTED.md](file:///c:/Users/KETAN%20TIWARI/Downloads/IBM/Sentinel-orbital-memory-/docs/GETTING_STARTED.md) for a step-by-step guide, including how to extend this with IBM Bob.

## Data Sources

All historical events in `data/historical_events.json` are sourced from public NASA/JPL/Goddard reports and reputable science journalism. Full citations are included in each event record.

## Status / Next Steps

This is an MVP prototype covering one flagship scenario (power/thermal degradation) end-to-end, complete with both a CLI output and a web UI dashboard cockpit. Natural next steps, time permitting:
- Support for additional anomaly scenarios and telemetry streams.
- Embeddings-based semantic search and vector retrieval for historical events.
- Advanced machine learning trained forecasting models (e.g. LSTM, Prophet) instead of linear extrapolation.
- Production deployment configuration and live WebSocket connections to streaming feeds.
