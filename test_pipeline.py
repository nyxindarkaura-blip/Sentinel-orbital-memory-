import unittest
import os
import sys

# Ensure src directory is in the path to import pipeline modules
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from sentinel import detect_and_diagnose, forecast_trajectory
from orbital_memory import find_similar_events, score_event
from synthesis import build_risk_card


class TestSentinelPipeline(unittest.TestCase):
    
    def setUp(self):
        # Generate a standard baseline telemetry stream (30 minutes of nominal data)
        self.nominal_readings = []
        for m in range(30):
            self.nominal_readings.append({
                "minute": m,
                "battery_voltage": 28.0,
                "current": 5.0,
                "temperature": 30.0
            })

    def test_what_nominal_no_anomaly(self):
        """Test 'WHAT' stage: Nominal telemetry should NOT trigger an anomaly."""
        # Add another nominal reading
        readings = self.nominal_readings + [{
            "minute": 30,
            "battery_voltage": 28.0,
            "current": 5.0,
            "temperature": 30.0
        }]
        
        result = detect_and_diagnose(readings, threshold_percent=5.0)
        
        self.assertFalse(result["anomaly_detected"], "Nominal readings should not trigger anomaly.")
        self.assertEqual(result["severity"], "Low")
        self.assertEqual(result["confidence"], 0)

    def test_what_anomaly_triggered(self):
        """Test 'WHAT' stage: Breaching 2 or more thresholds triggers an anomaly."""
        # Add anomalous reading (current rises +20%, temperature rises +15%, voltage stable)
        readings = self.nominal_readings + [{
            "minute": 30,
            "battery_voltage": 28.0,
            "current": 6.0,  # (6.0 - 5.0)/5.0 * 100 = 20% increase
            "temperature": 34.5  # (34.5 - 30.0)/30.0 * 100 = 15% increase
        }]
        
        result = detect_and_diagnose(readings, threshold_percent=5.0)
        
        self.assertTrue(result["anomaly_detected"], "Breaching two signals should trigger an anomaly.")
        self.assertEqual(result["severity"], "High")  # total magnitude 35 >= 25 is High
        self.assertGreater(result["confidence"], 50)

    def test_why_diagnosis_signals(self):
        """Test 'WHY' stage: Diagnosis accurately flags breached signals and percentages."""
        readings = self.nominal_readings + [{
            "minute": 30,
            "battery_voltage": 26.6,  # (26.6 - 28.0)/28.0 * 100 = -5.0% (decline)
            "current": 5.5,           # (5.5 - 5.0)/5.0 * 100 = 10.0% (increase)
            "temperature": 30.0       # stable
        }]
        
        result = detect_and_diagnose(readings, threshold_percent=5.0)
        
        flagged_signals = dict(result["flagged_signals"])
        self.assertIn("battery_voltage", flagged_signals)
        self.assertEqual(flagged_signals["battery_voltage"], -5.0)
        
        self.assertIn("current", flagged_signals)
        self.assertEqual(flagged_signals["current"], 10.0)
        
        self.assertNotIn("temperature", flagged_signals)

    def test_what_if_forecasting(self):
        """Test 'WHAT-IF' stage: Linearly forecasts telemetry values correctly."""
        # Create a line of increasing temperature (+1.0 degree/minute) for the last 15 minutes
        readings = []
        for m in range(30):
            readings.append({
                "minute": m,
                "battery_voltage": 28.0,
                "current": 5.0,
                "temperature": 30.0 + float(m)  # Rising linearly
            })
            
        # Last reading (minute 29): Temp is 59.0
        # Second to last in lookback window (minute 15): Temp is 45.0
        # Elapsed: 14 mins. Rate: (59.0 - 45.0) / 14 = 1.0 degree/min
        forecast_res = forecast_trajectory(readings, lookback_minutes=15)
        
        self.assertEqual(forecast_res["rates_per_minute"]["temperature"], 1.0)
        
        # 30 mins ahead projection: 59.0 + (1.0 * 30) = 89.0
        self.assertEqual(forecast_res["forecast"][30]["temperature"], 89.0)
        # 60 mins ahead projection: 59.0 + (1.0 * 60) = 119.0
        self.assertEqual(forecast_res["forecast"][60]["temperature"], 119.0)

    def test_what_now_matching_synthesis(self):
        """Test 'WHAT-NOW' stage: Sourced historical lessons are accurately paired and synthesized."""
        flagged_signals = [("battery_voltage", -10.0), ("temperature", 15.0)]
        
        # 1. Test Orbital Memory matches MGS correctly
        matches = find_similar_events(flagged_signals)
        self.assertGreater(len(matches), 0, "Should find matching events.")
        
        top_event, score = matches[0]
        self.assertEqual(top_event["id"], "MGS-2006")
        self.assertEqual(score, 100) # Both battery_voltage and temperature keywords matched MGS text
        
        # 2. Test Synthesis constructs risk card with recommendation citing MGS lesson
        sentinel_result = {
            "diagnosis": {
                "anomaly_detected": True,
                "severity": "High",
                "confidence": 90,
                "flagged_signals": flagged_signals,
                "latest_reading": {"minute": 30, "battery_voltage": 25.2, "current": 5.0, "temperature": 34.5},
                "baseline": {"battery_voltage": 28.0, "current": 5.0, "temperature": 30.0},
                "changes_percent": {"battery_voltage": -10.0, "current": 0.0, "temperature": 15.0}
            },
            "forecast": {
                "trend": "Worsening",
                "forecast": {
                    30: {"battery_voltage": 22.0, "current": 5.0, "temperature": 39.0},
                    60: {"battery_voltage": 19.0, "current": 5.0, "temperature": 43.5}
                }
            }
        }
        
        card = build_risk_card(sentinel_result, matches)
        self.assertEqual(card["combined_risk"], "Elevated Risk")
        self.assertIn("Review battery voltage, temperature", card["recommendation"])
        self.assertIn("Mars Global Surveyor", card["recommendation"])
        self.assertIn("A subtle, seemingly unrelated latent fault", card["recommendation"])
        self.assertIn("https://www.jpl.nasa.gov", card["sources"][0])


if __name__ == "__main__":
    unittest.main()
