"""
synthesis.py
------------
This is the "neither idea can do this alone" layer. It takes SENTINEL's
live diagnosis + forecast and ORBITAL MEMORY's historical matches, and
combines them into ONE evidence-grounded risk card -- the WHAT / WHY /
WHAT-IF / WHAT-NOW structure the team designed.

No new claims are invented here: every statement in the output is either
(a) a number computed directly from the telemetry, or (b) a fact pulled
directly from a specific historical event record. This is the guard
against hallucination that Melissa flagged as a key risk.
"""


def build_risk_card(sentinel_result, historical_matches):
    diagnosis = sentinel_result["diagnosis"]
    forecast = sentinel_result["forecast"]

    flagged_names = [name for name, _ in diagnosis["flagged_signals"]]

    # WHAT: what SENTINEL detected, in plain language
    what = (
        f"Anomaly detected in: {', '.join(flagged_names)}. "
        f"Severity: {diagnosis['severity']}. Confidence: {diagnosis['confidence']}%."
        if diagnosis["anomaly_detected"]
        else "No anomaly currently detected -- telemetry within normal range."
    )

    # WHY: which signals are driving it, with the actual percentage changes
    why_lines = []
    for name, pct in diagnosis["flagged_signals"]:
        direction = "declining" if pct < 0 else "rising"
        why_lines.append(f"{name.replace('_', ' ')} {direction} ({pct}% vs. baseline)")
    why = "; ".join(why_lines) if why_lines else "No contributing signals flagged."

    # WHAT-IF: SENTINEL's forecast
    what_if = (
        f"Trend: {forecast['trend']}. "
        f"If this continues, projected in 30 min: {forecast['forecast'][30]}; "
        f"in 60 min: {forecast['forecast'][60]}."
    )

    # Historical evidence from ORBITAL MEMORY
    evidence_lines = []
    escalated_count = 0
    for event, score in historical_matches:
        escalated = "escalat" in event["outcome"].lower() or "loss" in event["outcome"].lower() or "fail" in event["outcome"].lower()
        if escalated:
            escalated_count += 1
        evidence_lines.append(
            f"- {event['mission']} ({event['date']}), similarity {score}%: {event['outcome']}"
        )

    # Combined risk level: escalate if SENTINEL sees a worsening trend AND
    # historical precedent shows this pattern has led to serious outcomes.
    if diagnosis["anomaly_detected"] and forecast["trend"] == "Worsening" and escalated_count >= 1:
        combined_risk = "Elevated Risk"
    elif diagnosis["anomaly_detected"]:
        combined_risk = "Moderate Risk"
    else:
        combined_risk = "Nominal"

    # WHAT-NOW: recommendation, grounded in the flagged signals + historical lesson
    if historical_matches:
        top_event = historical_matches[0][0]
        recommendation = (
            f"Review {', '.join(n.replace('_', ' ') for n in flagged_names)} and non-essential power loads. "
            f"This pattern resembles {top_event['mission']} ({top_event['date']}), where the recorded lesson was: "
            f"\"{top_event['lesson']}\""
        )
    else:
        recommendation = "Continue monitoring; no closely matching historical precedent found in the curated Mission Memory."

    return {
        "combined_risk": combined_risk,
        "what": what,
        "why": why,
        "what_if": what_if,
        "historical_evidence": evidence_lines,
        "recommendation": recommendation,
        "sources": [s for event, _ in historical_matches for s in event.get("source", [])],
    }


def print_risk_card(card):
    """Pretty-print the risk card the way it would appear in a demo UI."""
    print("=" * 60)
    print(f"  RISK LEVEL: {card['combined_risk']}")
    print("=" * 60)
    print(f"\nWHAT happened?\n  {card['what']}")
    print(f"\nWHY is it happening?\n  {card['why']}")
    print(f"\nWHAT happens if it continues?\n  {card['what_if']}")
    print(f"\nHistorical evidence (ORBITAL MEMORY):")
    if card["historical_evidence"]:
        for line in card["historical_evidence"]:
            print(f"  {line}")
    else:
        print("  No matching historical events found.")
    print(f"\nWHAT should we do now?\n  {card['recommendation']}")
    print(f"\nSources:")
    for s in set(card["sources"]):
        print(f"  - {s}")
    print()
