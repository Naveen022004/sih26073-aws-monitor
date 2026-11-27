# Intelligent AWS Anomaly Detection System

A Streamlit-based academic prototype for exploring anomaly detection in Automatic Weather Station (AWS) observations. It combines rule-based sensor validation with an Isolation Forest model to flag unusual temperature, pressure, and humidity readings.

> **Project status:** Academic prototype for SIH26073. It does not connect to live AWS hardware or an operational weather service. Fault-injection scenarios are simulated for demonstration and testing.

## Table of contents

- [Overview](#overview)
- [Key features](#key-features)
- [How it works](#how-it-works)
- [Technology stack](#technology-stack)
- [Project structure](#project-structure)
- [Dataset format](#dataset-format)
- [Getting started](#getting-started)
- [Deploy on Streamlit Community Cloud](#deploy-on-streamlit-community-cloud)
- [Using the dashboard](#using-the-dashboard)
- [Limitations and responsible interpretation](#limitations-and-responsible-interpretation)
- [Roadmap](#roadmap)
- [Author](#author)

## Overview

Automatic Weather Stations collect environmental observations that need to be checked for sensor errors and unusual values. This project demonstrates a hybrid approach to flagging potentially abnormal observations and presenting the results in an interactive dashboard.

The prototype monitors three parameters:

| Parameter | Unit |
|---|---|
| Temperature | °C |
| Atmospheric pressure | hPa |
| Relative humidity | % |

## Key features

- **Interactive dashboard:** View the latest observation, telemetry history, charts, and anomaly audit log.
- **Hybrid detection:** Combine physical-boundary and temporal checks with an Isolation Forest baseline model.
- **Demonstration scenarios:** Test a temperature spike, frozen sensor, out-of-range humidity, and gradual weather change.
- **Estimated replacement values:** Display rolling-median estimates for flagged readings.
- **Data upload:** Load a historical CSV as the model baseline.
- **Export:** Download session telemetry as a CSV file.
- **Session audit trail:** Review flagged observations, severity, confidence, and explanations.

## How it works

The current prototype follows this processing flow:

1. Load the bundled baseline CSV or upload a historical dataset.
2. Validate the required columns and retain rows with valid numeric readings.
3. Fit an Isolation Forest model to the baseline temperature, pressure, and humidity values.
4. Process the next baseline observation when the user clicks **Generate next reading**.
5. Apply hard physical limits and temporal checks, followed by multivariate model and dew-point consistency checks.
6. Display the result, estimated replacement values, charts, and session audit information.

The dashboard's scenario selector can inject test values into observations. These are controlled demonstrations, not faults collected from physical sensors.

## Technology stack

- Python
- Streamlit
- pandas and NumPy
- scikit-learn (Isolation Forest)
- Plotly

## Project structure

```text
sih26073-aws-monitor/
├── app.py                 # Streamlit dashboard and session workflow
├── detector.py            # Hybrid anomaly detection logic
├── sample_aws_data.csv    # Bundled baseline/example dataset
├── requirements.txt       # Python dependencies
└── README.md
```

## Dataset format

Upload a CSV containing at least 10 valid rows and these numeric columns:

```csv
temperature,pressure,humidity
24.5,1012.8,62.0
25.1,1012.4,60.5
```

- `temperature`: degrees Celsius
- `pressure`: hectopascals (hPa)
- `humidity`: relative humidity in percent

A timestamp column is optional. Rows with missing or non-numeric values in the three required columns are excluded during loading.

**Data provenance matters:** Verify the source, station identity, units, collection period, and quality of any uploaded dataset before describing it as real AWS observations. The bundled CSV should not be presented as verified operational Indian AWS data unless its provenance has been independently established.

## Getting started

### Prerequisites

- Python 3.10 or later
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Naveen022004/sih26073-aws-monitor.git
cd sih26073-aws-monitor
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

Open the local URL printed in the terminal (usually http://localhost:8501).

## Deploy on Streamlit Community Cloud

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
2. Select **Create app**.
3. Choose repository `Naveen022004/sih26073-aws-monitor`.
4. Select branch `main` and main file path `app.py`.
5. Deploy and review the application logs if dependency installation or startup fails.

**Live demo:** No verified public app URL is listed yet. Add the deployed application URL here after confirming that it is publicly accessible.

## Using the dashboard

1. Start the Streamlit app.
2. Choose a demonstration station label in the sidebar.
3. Optionally upload a CSV and select **Load uploaded baseline**.
4. Select a test scenario.
5. Click **Generate next reading**.
6. Review the latest status, charts, telemetry history, and anomaly audit log.
7. Use **Download telemetry CSV** to export the current session.

The station labels are demonstration labels; they do not establish a connection to the named physical locations.

## Limitations and responsible interpretation

- The application is a prototype and does not ingest live AWS telemetry.
- Fault scenarios are simulated; they are not verified sensor-fault events.
- The Isolation Forest model is fitted to the selected baseline. Its output depends on the representativeness and quality of that data.
- The configured physical limits and rate-of-change thresholds are demonstration settings, not universal meteorological standards.
- The displayed confidence and health index are prototype indicators, not calibrated probabilities or certified sensor-reliability measurements.
- Rolling-median replacement values are estimates and should not be treated as recovered ground-truth observations.
- Operational use would require representative labelled datasets, station-specific calibration, validation, monitoring, and domain-expert review.

## Roadmap

- Validate the detector using traceable, labelled AWS observations.
- Add station metadata, configurable sensor limits, and unit validation.
- Evaluate detection performance with suitable metrics and documented test data.
- Expand fault explanations and sensor-specific diagnostics.
- Add automated tests and publish a verified live demonstration.

## Author

**Naveen Sindhu**  
[GitHub: @Naveen022004](https://github.com/Naveen022004)
