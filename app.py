import time

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from detector import AWSIntelligentDetector

st.set_page_config(
    page_title="SIH26073 | AWS Anomaly Intelligence",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

FEATURES = ["temperature", "pressure", "humidity"]
DEFAULT_DATA = "sample_aws_data.csv"
MAX_LOG_ROWS = 300


def load_baseline(uploaded_file=None):
    """Load and validate the station's historical CSV data."""
    source = uploaded_file if uploaded_file is not None else DEFAULT_DATA
    try:
        frame = pd.read_csv(source)
    except FileNotFoundError as exc:
        raise ValueError(
            "sample_aws_data.csv was not found. Put it beside app.py or upload a CSV."
        ) from exc
    except Exception as exc:
        raise ValueError(f"Could not read the CSV file: {exc}") from exc

    missing = [column for column in FEATURES if column not in frame.columns]
    if missing:
        raise ValueError("CSV is missing required columns: " + ", ".join(missing))

    for column in FEATURES:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=FEATURES).reset_index(drop=True)

    if len(frame) < 10:
        raise ValueError("At least 10 valid rows are required to train the baseline.")

    return frame


def initialise(data):
    detector = AWSIntelligentDetector()
    detector.fit_baseline(data[FEATURES].to_dict(orient="records"))
    st.session_state.detector = detector
    st.session_state.baseline = data
    st.session_state.stream_log = []
    st.session_state.alert_log = []
    st.session_state.step = 0
    st.session_state.last_reading = None


def next_reading(scenario):
    """Get the next baseline observation and optionally inject a test fault."""
    data = st.session_state.baseline
    row = data.iloc[st.session_state.step % len(data)]
    st.session_state.step += 1

    reading = {key: float(row[key]) for key in FEATURES}
    if scenario == "Temperature sensor spike (+20 °C)":
        reading["temperature"] += 20.0
    elif scenario == "Humidity out of range (120%)":
        reading["humidity"] = 120.0
    elif scenario == "Frozen sensor":
        history = st.session_state.detector.history
        if history:
            frozen = history[-1].copy()
            # Prepare a reproducible frozen-bus test for the detector's
            # three-frame comparison without indexing a short history.
            while len(history) < 3:
                history.insert(0, frozen.copy())
            history[-3:] = [frozen.copy(), frozen.copy(), frozen.copy()]
            reading = frozen.copy()
    elif scenario == "Storm-front test (gradual valid change)":
        previous = st.session_state.last_reading or reading
        reading = {
            "temperature": max(-5.0, previous["temperature"] - 0.4),
            "pressure": previous["pressure"] - 0.3,
            "humidity": min(99.0, previous["humidity"] + 1.5),
        }

    return reading


def process_one_frame(scenario):
    reading = next_reading(scenario)
    result = st.session_state.detector.process_realtime_reading(reading)
    is_anomaly, severity, confidence, cause, explanation, healed = result

    record = {
        "Timestamp": pd.Timestamp.now(),
        "Raw_Temp": reading["temperature"],
        "Raw_Pres": reading["pressure"],
        "Raw_Hum": reading["humidity"],
        "Healed_Temp": healed["temperature"],
        "Healed_Pres": healed["pressure"],
        "Healed_Hum": healed["humidity"],
        "Anomaly": bool(is_anomaly),
        "Severity": float(severity),
        "Confidence": float(confidence),
        "Root_Cause": cause,
        "Explanation": explanation,
        "Scenario": scenario,
    }
    st.session_state.stream_log.append(record)
    st.session_state.stream_log = st.session_state.stream_log[-MAX_LOG_ROWS:]
    if is_anomaly:
        st.session_state.alert_log.insert(0, record)
        st.session_state.alert_log = st.session_state.alert_log[:MAX_LOG_ROWS]
    st.session_state.last_reading = reading


st.title("🌦️ Intelligent AWS Anomaly & Sensor Health Monitor")
st.caption(
    "SIH26073 · Hybrid rule-based checks and Isolation Forest baseline detection"
)

# Initialise from the bundled CSV, or let the user provide their own dataset.
if "detector" not in st.session_state:
    try:
        initialise(load_baseline())
        st.session_state.data_source = DEFAULT_DATA
    except ValueError as error:
        st.error(str(error))
        st.stop()

with st.sidebar:
    st.header("Station controls")
    station_id = st.selectbox(
        "Station node",
        ["AWS-PB-01 (Ludhiana)", "AWS-HP-04 (Shimla)", "AWS-RJ-09 (Jodhpur)"],
    )
    st.caption("The selected station label is for dashboard demonstration.")

    uploaded = st.file_uploader("Use another historical CSV", type=["csv"])
    if st.button("Load uploaded baseline", use_container_width=True):
        if uploaded is None:
            st.warning("Choose a CSV file first.")
        else:
            try:
                new_data = load_baseline(uploaded)
                initialise(new_data)
                st.session_state.data_source = uploaded.name
                st.success(f"Loaded {len(new_data)} valid rows.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))

    st.divider()
    st.subheader("Test scenario")
    scenario = st.selectbox(
        "Next observation",
        [
            "Normal observation",
            "Temperature sensor spike (+20 °C)",
            "Frozen sensor",
            "Humidity out of range (120%)",
            "Storm-front test (gradual valid change)",
        ],
    )
    generate = st.button(
        "▶ Generate next reading", type="primary", use_container_width=True
    )
    if st.button("Reset telemetry", use_container_width=True):
        current_data = st.session_state.baseline
        initialise(current_data)
        st.rerun()

if generate:
    process_one_frame(scenario)

detector = st.session_state.detector
logs = st.session_state.stream_log
latest = logs[-1] if logs else None
health_score = max(
    0.0,
    round(
        100.0
        * (1.0 - detector.fault_count / max(1, detector.total_frames)),
        1,
    ),
)

st.caption(
    f"Active node: **{station_id}** · Baseline: **{st.session_state.data_source}** "
    f"· {len(st.session_state.baseline)} valid observations"
)

m1, m2, m3, m4 = st.columns(4)
if latest:
    m1.metric("🌡️ Temperature", f"{latest['Raw_Temp']:.2f} °C")
    m2.metric("⏲️ Pressure", f"{latest['Raw_Pres']:.2f} hPa")
    m3.metric("💧 Humidity", f"{latest['Raw_Hum']:.2f} %")
else:
    m1.metric("🌡️ Temperature", "—")
    m2.metric("⏲️ Pressure", "—")
    m3.metric("💧 Humidity", "—")
m4.metric("🩺 Sensor health index", f"{health_score:.1f}%")

if latest:
    if latest["Anomaly"]:
        st.error(
            f"🚨 **{latest['Root_Cause']}** · Severity: "
            f"**{latest['Severity']:.2f}** · Confidence: "
            f"**{latest['Confidence']:.0%}**\n\n"
            f"**Explanation:** {latest['Explanation']}\n\n"
            f"**Estimated replacement:** T={latest['Healed_Temp']:.2f} °C, "
            f"P={latest['Healed_Pres']:.2f} hPa, H={latest['Healed_Hum']:.2f}%"
        )
    else:
        st.success(f"✅ **No anomaly flagged.** {latest['Explanation']}")
else:
    st.info("Choose a test scenario and click **Generate next reading** to begin.")

if logs:
    stream = pd.DataFrame(logs)
    left, right = st.columns(2)

    with left:
        fig_temp = go.Figure()
        fig_temp.add_trace(
            go.Scatter(
                x=stream["Timestamp"], y=stream["Raw_Temp"],
                mode="lines+markers", name="Observed temperature",
            )
        )
        fig_temp.add_trace(
            go.Scatter(
                x=stream["Timestamp"], y=stream["Healed_Temp"],
                mode="lines", name="Estimated replacement",
                line={"dash": "dash"},
            )
        )
        fig_temp.update_layout(
            title="Temperature: observed vs estimated",
            height=340, xaxis_title="Time", yaxis_title="°C",
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    with right:
        fig_ph = go.Figure()
        fig_ph.add_trace(
            go.Scatter(
                x=stream["Timestamp"], y=stream["Raw_Pres"],
                mode="lines+markers", name="Pressure (hPa)",
            )
        )
        fig_ph.add_trace(
            go.Scatter(
                x=stream["Timestamp"], y=stream["Raw_Hum"],
                mode="lines+markers", name="Humidity (%)",
                yaxis="y2",
            )
        )
        fig_ph.update_layout(
            title="Pressure and relative humidity",
            height=340,
            yaxis={"title": "hPa"},
            yaxis2={"title": "%", "overlaying": "y", "side": "right"},
        )
        st.plotly_chart(fig_ph, use_container_width=True)

    st.subheader("Telemetry history")
    st.dataframe(stream.sort_values("Timestamp", ascending=False), use_container_width=True)
    st.download_button(
        "Download telemetry CSV",
        data=stream.to_csv(index=False).encode("utf-8"),
        file_name="aws_telemetry_log.csv",
        mime="text/csv",
    )

st.subheader("🚨 Anomaly audit log")
if st.session_state.alert_log:
    alerts = pd.DataFrame(st.session_state.alert_log)
    st.dataframe(
        alerts[
            ["Timestamp", "Scenario", "Root_Cause", "Severity", "Confidence",
             "Raw_Temp", "Raw_Pres", "Raw_Hum", "Explanation"]
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No anomalies have been recorded in this session.")

with st.expander("About this prototype and its data"):
    st.write(
        "The dashboard trains an Isolation Forest model on the supplied CSV and "
        "combines its output with rule-based sensor checks. Test scenarios are "
        "simulated fault injections, not live station telemetry. Verify the "
        "provenance of the baseline CSV before presenting it as real AWS data."
    )
