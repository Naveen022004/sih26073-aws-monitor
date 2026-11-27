# Intelligent AWS Anomaly Detection System

A Streamlit prototype for exploring anomaly detection in Automatic Weather Station (AWS) observations. The project combines configurable rule-based checks with an Isolation Forest model to flag unusual sensor readings and present an auditable monitoring workflow.

> **Project status:** Academic prototype. It is not connected to live AWS hardware or an operational weather service. Fault-injection scenarios are simulated for testing.

## Highlights

- Streamlit dashboard for inspecting station observations.
- Hybrid detection pipeline: rule-based validation plus Isolation Forest.
- Charts, anomaly status, and a session audit log.
- CSV export for the telemetry generated during a session.
- CSV upload for testing with another baseline dataset.
- Demonstration scenarios for spikes, frozen readings, out-of-range humidity, and gradual weather changes.

## Screenshots

No verified UI screenshots are currently stored in this repository. Add genuine captures under `docs/screenshots/` and embed them here, for example:

- `docs/screenshots/dashboard.png` — main dashboard
- `docs/screenshots/anomaly-alert.png` — detected anomaly and explanation
- `docs/screenshots/audit-log.png` — event history and export

## Tech Stack

Python · Streamlit · pandas · NumPy · scikit-learn · Plotly

## Repository Layout

```text
.
├── app.py                 # Streamlit dashboard and user interactions
├── detector.py            # Hybrid anomaly detection logic
├── sample_aws_data.csv    # Example baseline dataset
├── requirements.txt       # Python dependencies
└── README.md
```

## Run Locally

**Requirements:** Python 3.10 or later is recommended.

```bash
git clone https://github.com/Naveen022004/sih26073-aws-monitor.git
cd sih26073-aws-monitor

python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies and start the app:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local address printed by Streamlit (usually http://localhost:8501).

## Deploy to Streamlit Community Cloud

1. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) using GitHub.
2. Choose **Create app**.
3. Select `Naveen022004/sih26073-aws-monitor`, branch `main`, and main file `app.py`.
4. Deploy and wait for dependency installation to finish.

**Live demo:** Not yet documented here. Add the public Streamlit app URL after deployment; do not use the profile URL as the app URL.

## How to Use

1. Launch the dashboard and choose a station label.
2. Select **Generate next reading** to process an observation.
3. Choose a demonstration scenario to test the detector.
4. Review the latest status, charts, and audit log.
5. Export session telemetry as CSV, or upload a compatible baseline CSV.

Uploaded datasets should contain numeric `temperature`, `pressure`, and `humidity` columns with at least 10 valid rows. A timestamp column is optional. Confirm dataset provenance, station identity, units, and quality before interpreting results.

## Limitations

- Demonstration fault scenarios are simulated, not real sensor faults.
- The bundled CSV should not be described as operational Indian AWS data unless its provenance is independently verified.
- The health indicator is a prototype summary, not a calibrated reliability score.
- Model outputs require validation against labelled, representative station data before operational use.

## Future Work

- Validate against traceable, labelled AWS observations.
- Add station metadata, sensor-specific thresholds, and unit validation.
- Improve fault explanations and model evaluation.
- Add automated tests and a documented live deployment.

## Author

**Naveen Sindhu** · [GitHub](https://github.com/Naveen022004)
