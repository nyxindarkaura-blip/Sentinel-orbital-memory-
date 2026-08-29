/**
 * script.js
 * ---------
 * Client-side script for the SENTINEL + ORBITAL MEMORY cockpit HUD dashboard.
 * Fetches JSON analysis from the backend Flask server, updates DOM readouts,
 * parses raw forecasts into visual comparative cards, and plots telemetry.
 */

// Active Chart.js instance tracking
let telemetryChart = null;
let currentSimulationMode = 'anomaly';

document.addEventListener("DOMContentLoaded", () => {
    // Bind button trigger clicks
    document.getElementById("btn-anomaly").addEventListener("click", () => triggerSimulation("anomaly"));
    document.getElementById("btn-nominal").addEventListener("click", () => triggerSimulation("nominal"));

    // Run initial simulation on load
    triggerSimulation("anomaly");
});

/**
 * Triggers a fetch call to the backend pipeline endpoint, then updates the HUD.
 * @param {string} mode - 'anomaly' or 'nominal'
 */
async function triggerSimulation(mode) {
    currentSimulationMode = mode;
    try {
        // Fast pulse on loading state
        const indicator = document.getElementById("system-status-indicator");
        indicator.style.animationDuration = "0.4s";


        const response = await fetch(`/api/simulate?mode=${mode}`);
        if (!response.ok) {
            throw new Error(`Server returned HTTP status ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update DOM elements with results
        updateHUD(data);
        
        // Restore normal pulse rate
        indicator.style.animationDuration = "1.8s";
        
    } catch (error) {
        console.error("Pipeline request failed:", error);
        alert(`Error executing simulation: ${error.message}`);
    }
}

/**
 * Updates the front-end dashboard panels with JSON pipeline results.
 * @param {object} data - The payload containing readings, sentinel_result, matches, and card.
 */
function updateHUD(data) {
    const card = data.card;
    const readings = data.readings;
    const sentinel = data.sentinel_result;
    const diagnosis = sentinel.diagnosis;
    const latest = diagnosis.latest_reading;
    const baseline = diagnosis.baseline;
    const changes = diagnosis.changes_percent;
    const flagged = diagnosis.flagged_signals.map(pair => pair[0]);

    // 1. Update Combined Risk Banner
    const banner = document.getElementById("risk-banner");
    const label = document.getElementById("risk-label");
    const riskIconSvg = document.getElementById("risk-icon-svg");
    
    banner.className = "risk-banner"; // reset
    if (card.combined_risk === "Nominal") {
        banner.classList.add("nominal-banner");
        label.textContent = "NOMINAL MONITORING ACTIVE | NOMINAL";
        // Inline Check Circle SVG
        riskIconSvg.innerHTML = `<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>`;
    } else if (card.combined_risk === "Moderate Risk") {
        banner.classList.add("moderate-banner");
        label.textContent = "MODERATE RISK ANOMALY DETECTED | MODERATE RISK";
        // Inline Warning SVG
        riskIconSvg.innerHTML = `<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>`;
    } else { // Elevated Risk
        banner.classList.add("elevated-banner");
        label.textContent = "ELEVATED SYSTEM RISK DETECTED | ELEVATED RISK";
        // Inline Critical Triangle SVG
        riskIconSvg.innerHTML = `<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>`;
    }

    // 2. Update Engine Status Cards
    const ratingText = document.getElementById("risk-rating");
    const statusText = document.getElementById("engine-status-text");
    const severityVal = document.getElementById("metric-severity");
    const confidenceVal = document.getElementById("metric-confidence");
    const progressFill = document.getElementById("confidence-progress");

    ratingText.textContent = card.combined_risk.toUpperCase();
    ratingText.className = "focal-value"; // reset

    if (card.combined_risk === "Nominal") {
        ratingText.classList.add("rating-nominal");
        statusText.textContent = "SYSTEM STATUS HEALTHY";
        
        severityVal.className = "metric-value text-green";
        severityVal.textContent = "Low";
        
        confidenceVal.style.color = "var(--accent-cyan)";
        confidenceVal.textContent = "0%";
        progressFill.style.width = "0%";
    } else if (card.combined_risk === "Moderate Risk") {
        ratingText.classList.add("rating-moderate");
        statusText.textContent = "MODERATE INCIDENT WARNING";
        
        severityVal.className = "metric-value text-amber";
        severityVal.textContent = diagnosis.severity;
        
        confidenceVal.style.color = "var(--accent-cyan)";
        confidenceVal.textContent = `${diagnosis.confidence}%`;
        progressFill.style.width = `${diagnosis.confidence}%`;
    } else {
        ratingText.classList.add("rating-elevated");
        statusText.textContent = "CRITICAL RISK ALARM";
        
        severityVal.className = "metric-value text-red";
        severityVal.textContent = diagnosis.severity;
        
        confidenceVal.style.color = "var(--accent-cyan)";
        confidenceVal.textContent = `${diagnosis.confidence}%`;
        progressFill.style.width = `${diagnosis.confidence}%`;
    }

    // 3. Update Live Telemetry Metrics with tabular badges
    updateMetricCard("voltage", latest.battery_voltage, "V", baseline.battery_voltage, changes.battery_voltage, flagged.includes("battery_voltage"));
    updateMetricCard("current", latest.current, "A", baseline.current, changes.current, flagged.includes("current"));
    updateMetricCard("temp", latest.temperature, "°C", baseline.temperature, changes.temperature, flagged.includes("temperature"));

    // 4. Update the 2x2 Risk Synthesis Cards
    document.getElementById("card-what").textContent = card.what;
    document.getElementById("card-why").textContent = card.why;
    document.getElementById("card-recommendation").textContent = card.recommendation;

    // Upgraded What-If (Projections): Parse the forecast JSON dictionary into comparison tables
    const forecast = sentinel.forecast;
    const cardWhatIf = document.getElementById("card-whatif");
    const f30 = forecast.forecast["30"];
    const f60 = forecast.forecast["60"];
    
    cardWhatIf.innerHTML = `
        <div style="margin-bottom: 12px; font-weight: 600;">
            TREND STATUS: <strong class="${forecast.trend === 'Worsening' ? 'text-red' : 'text-green'}">${forecast.trend.toUpperCase()}</strong>
        </div>
        <div class="projection-container">
            <div class="projection-card">
                <div class="projection-card-title">T + 30 MIN HORIZON</div>
                <div class="projection-row"><span>Voltage:</span><span class="projection-val">${f30.battery_voltage.toFixed(2)}V</span></div>
                <div class="projection-row"><span>Current:</span><span class="projection-val">${f30.current.toFixed(2)}A</span></div>
                <div class="projection-row"><span>Temperature:</span><span class="projection-val">${f30.temperature.toFixed(2)}°C</span></div>
            </div>
            <div class="projection-card">
                <div class="projection-card-title">T + 60 MIN HORIZON</div>
                <div class="projection-row"><span>Voltage:</span><span class="projection-val">${f60.battery_voltage.toFixed(2)}V</span></div>
                <div class="projection-row"><span>Current:</span><span class="projection-val">${f60.current.toFixed(2)}A</span></div>
                <div class="projection-row"><span>Temperature:</span><span class="projection-val">${f60.temperature.toFixed(2)}°C</span></div>
            </div>
        </div>
    `;

    // 5. Update Historical Evidence Match Cards
    renderHistoricalMatches(data.matches);

    // 6. Update Citation/Grounding References
    renderSources(card.sources);

    // 7. Re-Plot the Telemetry Stream
    renderChart(readings);

    // 8. Fire update animations
    triggerTransition();
}

/**
 * Updates a single telemetry metric block.
 */
function updateMetricCard(idSuffix, value, unit, baselineVal, percentChange, isAlarmed) {
    const cardEl = document.getElementById(`metric-${idSuffix}`);
    const valEl = document.getElementById(`val-${idSuffix}`);
    const baseEl = document.getElementById(`base-${idSuffix}`);
    const changeEl = document.getElementById(`change-${idSuffix}`);
    const labelEl = document.getElementById(`label-${idSuffix}`);

    // Update numbers
    valEl.textContent = value.toFixed(2);
    baseEl.textContent = baselineVal.toFixed(2);
    
    const sign = percentChange > 0 ? "+" : "";
    changeEl.textContent = `${sign}${percentChange}%`;

    // Reset styles
    cardEl.className = "metric-card glass-card";
    changeEl.className = "delta-badge"; // reset
    
    // Set appropriate colors and warning alerts
    let isBad = false;
    if (idSuffix === "voltage") {
        isBad = percentChange < 0;
    } else { // current and temperature
        isBad = percentChange > 0;
    }

    if (isBad) {
        changeEl.classList.add("delta-red");
    } else {
        changeEl.classList.add("delta-green");
    }

    if (isAlarmed) {
        cardEl.classList.add("alarmed");
        labelEl.innerHTML = `<span class="alarm-pulse"></span>${idSuffix.toUpperCase()}`;
    } else {
        labelEl.innerHTML = idSuffix.charAt(0).toUpperCase() + idSuffix.slice(1);
    }
}

/**
 * Populates similar spacecraft incidents matches with metadata chips.
 */
function renderHistoricalMatches(matches) {
    const container = document.getElementById("historical-precedents-container");
    container.innerHTML = ""; // Clear existing

    if (!matches || matches.length === 0) {
        container.innerHTML = `
            <div class="glass-card" style="text-align: center; color: var(--text-muted); padding: 30px;">
                🟢 System is nominal. No corresponding historical anomaly matches found in Orbital Memory.
            </div>
        `;
        return;
    }

    matches.forEach(match => {
        const event = match[0];
        const score = match[1];
        
        const patternHtml = event.telemetry_pattern.map(pat => `<li>${pat}</li>`).join("");

        const cardHtml = `
            <div class="historical-card">
                <div class="historical-header">
                    <span class="historical-title">🚀 ${event.mission}</span>
                    <span class="historical-score">${score}% SIMILARITY</span>
                </div>
                
                <!-- Tagged Metadata Chips Upgrade -->
                <div class="meta-tag-container">
                    <span class="meta-tag">AGENCY: ${event.agency}</span>
                    <span class="meta-tag">INCIDENT DATE: ${event.date}</span>
                    <span class="meta-tag">SUBSYSTEM: ${event.subsystem}</span>
                </div>
                
                <div class="historical-section" style="margin-bottom: 12px;">
                    <div style="font-size: 0.95rem; line-height: 1.5; color: #e2e8f0;">
                        <strong>Incident Summary:</strong> ${event.summary}
                    </div>
                </div>
                <div class="historical-card-grid">
                    <div>
                        <div class="historical-section-label">📉 Historical Telemetry Pattern</div>
                        <ul class="historical-bullets">
                            ${patternHtml}
                        </ul>
                    </div>
                    <div>
                        <div class="historical-section-label">🔍 Root Cause</div>
                        <div class="historical-section-val">${event.root_cause}</div>
                    </div>
                </div>
                <div class="historical-card-grid">
                    <div>
                        <div class="historical-section-label">💥 Incident Outcome</div>
                        <div class="historical-section-val" style="color: var(--accent-red); font-weight: 500;">${event.outcome}</div>
                    </div>
                    <div>
                        <div class="historical-section-label">💡 Lesson Learned</div>
                        <div class="historical-section-val" style="color: var(--accent-green); font-weight: 500;">${event.lesson}</div>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML += cardHtml;
    });
}

/**
 * Populates citations and references list.
 */
function renderSources(sources) {
    const container = document.getElementById("sources-list");
    container.innerHTML = "";

    if (!sources || sources.length === 0) {
        container.innerHTML = "<div>No grounding sources available under current Nominal telemetry status.</div>";
        return;
    }

    // Filter duplicates
    const uniqueSources = [...new Set(sources)];
    uniqueSources.forEach((source, idx) => {
        container.innerHTML += `<div>[${idx + 1}] ${source}</div>`;
    });
}

/**
 * Draws the high-tech glowing telemetry chart using Chart.js.
 */
function renderChart(readings) {
    const minutes = readings.map(r => r.minute);
    const voltage = readings.map(r => r.battery_voltage);
    const current = readings.map(r => r.current);
    const temp = readings.map(r => r.temperature);

    const ctx = document.getElementById("telemetryChart").getContext("2d");

    if (telemetryChart) {
        telemetryChart.destroy();
    }

    telemetryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: minutes,
            datasets: [
                {
                    label: 'Battery Voltage (V)',
                    data: voltage,
                    borderColor: '#0ea5e9',
                    backgroundColor: 'rgba(14, 165, 233, 0.02)',
                    borderWidth: 2.5,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    tension: 0.2,
                    fill: true
                },
                {
                    label: 'Current (A)',
                    data: current,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.02)',
                    borderWidth: 2.5,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    tension: 0.2,
                    fill: true
                },
                {
                    label: 'Temperature (°C)',
                    data: temp,
                    borderColor: '#f43f5e',
                    backgroundColor: 'rgba(244, 63, 94, 0.02)',
                    borderWidth: 2.5,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    tension: 0.2,
                    fill: true
                }
            ]
        },
        plugins: [{
            id: 'anomalyZoneHighlight',
            beforeDraw: (chart) => {
                if (currentSimulationMode === 'anomaly') {
                    const ctx = chart.ctx;
                    const xAxis = chart.scales.x;
                    const yAxis = chart.scales.y;
                    
                    const xStart = xAxis.getPixelForValue(30);
                    const xEnd = xAxis.getPixelForValue(60);
                    
                    const yTop = yAxis.top;
                    const yBottom = yAxis.bottom;
                    
                    ctx.save();
                    
                    // Shaded transparent red anomaly band
                    ctx.fillStyle = 'rgba(244, 63, 94, 0.07)';
                    ctx.fillRect(xStart, yTop, xEnd - xStart, yBottom - yTop);
                    
                    // Left boundary line (dashed)
                    ctx.strokeStyle = 'rgba(244, 63, 94, 0.4)';
                    ctx.lineWidth = 1.5;
                    ctx.setLineDash([4, 4]);
                    ctx.beginPath();
                    ctx.moveTo(xStart, yTop);
                    ctx.lineTo(xStart, yBottom);
                    ctx.stroke();
                    
                    // Label
                    ctx.fillStyle = 'rgba(244, 63, 94, 0.8)';
                    ctx.font = 'bold 10px "Inter", sans-serif';
                    ctx.textBaseline = 'top';
                    ctx.textAlign = 'left';
                    ctx.fillText('ANOMALY ACTIVE', xStart + 8, yTop + 8);
                    
                    ctx.restore();
                }
            }
        }],
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        font: {
                            family: "'Inter', sans-serif",
                            size: 11,
                            weight: 600
                        },
                        boxWidth: 15
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#0c1020',
                    borderColor: 'rgba(14, 165, 233, 0.25)',
                    borderWidth: 1,
                    titleColor: '#ffffff',
                    bodyColor: '#cbd5e1',
                    titleFont: { family: "'JetBrains Mono', monospace", size: 11 },
                    bodyFont: { family: "'JetBrains Mono', monospace", size: 11 }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.03)',
                        drawTicks: false
                    },
                    ticks: {
                        color: '#64748b',
                        font: { family: "'JetBrains Mono', monospace", size: 9 }
                    },
                    title: {
                        display: true,
                        text: 'Time (minutes)',
                        color: '#64748b',
                        font: { family: "'Inter', sans-serif", size: 11, weight: 600 }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.03)',
                        drawTicks: false
                    },
                    ticks: {
                        color: '#64748b',
                        font: { family: "'JetBrains Mono', monospace", size: 9 }
                    },
                    title: {
                        display: true,
                        text: 'Telemetry Sensor Readout',
                        color: '#64748b',
                        font: { family: "'Inter', sans-serif", size: 11, weight: 600 }
                    }
                }
            }
        }
    });
}

/**
 * Triggers the slide-up fade animations when data updates.
 */
function triggerTransition() {
    const cards = document.querySelectorAll(".glass-card, .historical-card");
    cards.forEach(card => {
        card.classList.remove("fade-transition");
        void card.offsetWidth; // Force CSS repaint/reflow
        card.classList.add("fade-transition");
    });
}
