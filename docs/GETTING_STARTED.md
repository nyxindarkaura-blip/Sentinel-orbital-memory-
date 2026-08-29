Setup & Development Guide

This guide covers installing dependencies, running the project locally, and working with it in IBM Bob.


Prerequisites


A desktop/laptop computer (Windows, macOS, or Linux)

Python 3.10+ installed, with "Add python.exe to PATH" checked during installation on Windows

IBM Bob installed and signed in with an IBMid


Verify Python is installed correctly by opening a terminal and running:


python --version

Running the Project Locally

Clone or download this repository.

### Option A: Running the Terminal Console Version
1. Open a terminal and navigate to the `src/` directory:
   ```bash
   cd src
   ```
2. Run the demo pipeline:
   ```bash
   python main.py
   ```
This runs the full pipeline end-to-end (telemetry simulation → SENTINEL → ORBITAL MEMORY → synthesis) and prints a risk card to the terminal, based on a scenario modeled on the real Mars Global Surveyor (2006) incident.

### Option B: Running the Web UI Dashboard Cockpit
1. Open a terminal in the root directory.
2. Install dependencies:
   ```bash
   pip install -r requirements-ui.txt
   ```
3. Run the Flask server:
   ```bash
   python server.py
   ```
4. Open http://localhost:5000 in your browser.



Working in IBM Bob


Open IBM Bob

Choose Open Folder and select this project's root directory

Open a terminal inside Bob and run the same command as above to confirm the pipeline runs correctly in that environment

From there, IBM Bob's AI assistant can be used to extend the project, for example:
- Adding support for streaming telemetry via WebSockets to the Web UI dashboard.
- Adding additional curated historical events to data/historical_events.json.
- Writing unit tests for the detection/forecasting logic.
- Extending telemetry_simulator.py to support additional anomaly scenarios.


Project Structure

├── README.md                    — root description and quick start
├── requirements.txt             — core pipeline dependencies
├── requirements-ui.txt          — UI dashboard dependencies (Flask)
├── server.py                    — Flask backend server serving UI and API
├── public/                      — frontend Web UI dashboard static files
│   ├── index.html               — main HTML structure
│   ├── style.css                — dashboard styles
│   └── script.js                — frontend telemetry visualization logic (Chart.js)
├── data/
│   └── historical_events.json   — curated historical mission events (Orbital Memory's dataset)
├── src/
│   ├── telemetry_simulator.py   — generates the demo telemetry stream
│   ├── sentinel.py               — detect, diagnose, forecast
│   ├── orbital_memory.py         — historical event retrieval
│   ├── synthesis.py              — combines both into the risk card
│   └── main.py                   — entry point for the end-to-end demo
└── docs/
    └── GETTING_STARTED.md        — this file

Troubleshooting


python not recognized / opens Microsoft Store instead of running: Python isn't installed, or wasn't added to PATH. Reinstall from python.org and ensure "Add python.exe to PATH" is checked, then open a new terminal window.

File upload issues on GitHub mobile: large or multi-file uploads can fail on mobile browsers due to memory limits. Upload files individually, clear browser cache, or use a desktop browser instead.
