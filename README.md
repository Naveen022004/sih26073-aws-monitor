# SIH26073: Intelligent AWS Anomaly Detection System

A Streamlit prototype for monitoring Automatic Weather Station (AWS) observations. It combines rule-based sensor checks with an Isolation Forest model trained on a historical CSV baseline.

## Project files

- `app.py` — Streamlit dashboard, telemetry simulation, charts, anomaly audit log and CSV export.
- `detector.py` — Hybrid anomaly detection engine.
- `sample_aws_data.csv` — Bundled example baseline. Verify its provenance before describing it as real operational AWS data.
- `requirements.txt` — Python dependencies.

## Run locally (Windows)

Open PowerShell in the repository folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation, run the install and launch commands using the venv executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed in the terminal (normally http://localhost:8501).

## Run on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Select **Create app** and choose `Naveen022004/sih26073-aws-monitor`.
4. Set the branch to `main` and the main file path to `app.py`.
5. Deploy. Streamlit Cloud installs packages from `requirements.txt`.

## Dashboard usage

1. Select a station label in the sidebar.
2. Click **Generate next reading** to process one observation from the baseline CSV.
3. Select a test scenario to inject a simulated fault:
   - Temperature sensor spike (+20 °C)
   - Frozen sensor
   - Humidity out of range (120%)
   - Storm-front test (gradual valid change)
4. Review the latest status, charts and anomaly audit log.
5. Download the session telemetry using **Download telemetry CSV**.
6. Upload another CSV baseline using the sidebar uploader. It must contain numeric `temperature`, `pressure`, and `humidity` columns and at least 10 valid rows. A timestamp column is optional.

## Important notes

- The dashboard processes one observation per button click; it does not run an uncontrolled infinite rerun loop.
- Fault injection scenarios are simulations for demonstration and testing, not live sensor readings.
- The health index is a simple prototype indicator based on flagged frames, not a calibrated reliability metric.
- The dew-point calculation in the detector should not be interpreted as proof of sensor fault without a physically valid cross-sensor model and domain validation.
- Confirm the source, units, station identity and quality of any uploaded dataset before using it for research or operational decisions.
