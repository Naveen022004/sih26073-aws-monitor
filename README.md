# SIH26073: Intelligent AWS Real-Time Anomaly Detection System

## Project Structure
Place all downloaded files in the same folder:
- `detector.py` — Hybrid AI + Thermodynamic anomaly detection, root-cause classification, and self-healing imputation engine.
- `app.py` — Real-time Streamlit dashboard with interactive fault injection and live telemetry charts.
- `sample_aws_data.csv` — Baseline historical Automatic Weather Station (AWS) dataset (Temperature, Pressure, Humidity).
- `requirements.txt` — Python package dependencies.

## Step-by-Step Setup & Execution Guide

### Step 1: Verify Python Installation
Ensure **Python 3.9+** is installed on your machine:
```bash
python --version
```

### Step 2: Create a Project Folder & Place Files
Create a new folder named `SIH26073_AWS_Monitor` and move `detector.py`, `app.py`, `sample_aws_data.csv`, and `requirements.txt` inside it.

### Step 3: Create and Activate a Virtual Environment (Recommended)
Open a terminal inside `SIH26073_AWS_Monitor` and run:
- **Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
Your default browser will automatically open at `http://localhost:8501`.

### Step 6: Live Demo & Testing Flow
1. Click **Start Stream** in the left sidebar to begin real-time weather ingestion.
2. Select **Simulate: Genuine Storm Front (Valid)** and click **Trigger Scenario Now** to demonstrate zero false alarms during real weather shifts.
3. Select **Inject: Temp Sensor Spike (+20°C)**, **Inject: Frozen Bus**, or **Inject: Dew Point Violation** and click **Trigger Scenario Now** to observe real-time alert classification, XAI root-cause explanations, sensor health degradation, and self-healed data imputation.
