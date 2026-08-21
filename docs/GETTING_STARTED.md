# Getting Started (Beginner-Friendly)

This guide assumes you've just finished a Python course and are using IBM Bob for the first time. No prior project experience needed.

## 1. Install IBM Bob

IBM Bob is a desktop app (built on VS Code) — you'll need a laptop or PC (Windows, macOS, or Linux). It won't run on a phone or tablet.

1. Go to the IBM Bob site and download the installer for your OS.
2. Run the installer (takes about 5 minutes).
3. Sign in with your IBMid when prompted (create one if you don't have it).
4. Open Bob — it should feel like a normal code editor (VS Code) with an AI assistant panel.

## 2. Get Python running on your machine

Check if Python is already installed by opening a terminal (in Bob, or your system terminal) and running:

```bash
python3 --version
```

If you see a version number (e.g. `Python 3.11.4`), you're set. If not, download Python from python.org and install it — the default installer options are fine.

## 3. Open this project in IBM Bob

1. In Bob, choose "Open Folder" and select the `sentinel_orbital_memory` folder.
2. You should see the `src/`, `data/`, and `docs/` folders in the sidebar.

## 4. Run the demo for the first time

Open a terminal inside Bob (there's usually a Terminal menu or panel) and run:

```bash
cd src
python3 main.py
```

You should see a "risk card" printed to the screen, ending with a recommendation that cites a real historical NASA incident (Mars Global Surveyor, 2006). If you see that — the whole pipeline works.

## 5. How to use IBM Bob to extend this project

This codebase is intentionally simple and heavily commented so you can read every file and understand what it does. From here, IBM Bob is your assistant for building on top of it. Some things you can ask Bob to help with, in plain English:

- *"Explain what sentinel.py does, function by function."* — good first step to build your own understanding before you present this.
- *"Add a Streamlit web UI that displays the risk card from synthesis.py in a browser instead of the terminal."* — this turns your console demo into something visual for the video.
- *"Add a fourth historical event to data/historical_events.json about [some other real incident] — help me structure it the same way as the existing ones."*
- *"Write a unit test for the detect_and_diagnose function in sentinel.py."*
- *"Refactor telemetry_simulator.py so it can also generate a comms-subsystem anomaly, not just power/thermal."* (only if you have time left after the core scenario is solid)

**Important for your submission:** the README asks you to document how IBM Bob was used. Keep a running note (even a rough one) each time Bob generates or changes something meaningful — you'll need this for the README and it'll help you explain your project confidently in the demo video.

## 6. Suggested order of work

1. Get `main.py` running exactly as-is (you've basically already done this if you followed this guide).
2. Read through `sentinel.py` and `orbital_memory.py` until you can explain them in your own words.
3. Ask Bob to help you build a simple UI on top of `synthesis.py`'s output (this is what you'll actually show in the demo video).
4. Polish the README's "How IBM Bob Was Used" section.
5. Record your 3-minute demo video.
6. Publish the GitHub repo (make sure it's public) and the project submission page.

## 7. If something breaks

Paste the exact error message into Bob (or back into this chat) and ask what it means and how to fix it — that's the fastest way to unblock yourself as a beginner. Don't spend more than 15–20 minutes stuck on any one error before asking for help.
