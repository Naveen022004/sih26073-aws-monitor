import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
from detector import AWSIntelligentDetector

st.set_page_config(
    page_title="SIH26073 | AWS Anomaly Intelligence",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State Setup
if "detector" not in st.session_state:
    try:
        df_hist = pd.read_csv("sample_aws_data.csv")
        baseline = df_hist[['temperature', 'pressure', 'humidity']].to_dict(orient="records")
    except Exception:
        np.random.seed(42)
        baseline = [
            {
                'temperature': round(24.0 + 4.0 * np.sin(i / 15.0) + np.random.normal(0, 0.15), 2),
                'pressure': round(1013.0 + 1.5 * np.cos(i / 20.0) + np.random.normal(0, 0.2), 2),
                'humidity': round(62.0 - 8.0 * np.sin(i / 15.0) + np.random.normal(0, 0.5), 2)
            }
            for i in range(120)
        ]

    det = AWSIntelligentDetector()
    det.fit_baseline(baseline)
    st.session_state.detector = det
    st.session_state.stream_log = []
    st.session_state.alert_log = []
    st.session_state.step = len(baseline)
    st.session_state.inject_fault = "None"
    st.session_state.running = False

# Sidebar Controls
with st.sidebar:
    st.header("🎛️ AWS Station Controls")
    station_id = st.selectbox(
        "Select Station Node",
        ["AWS-PB-01 (Ludhiana)", "AWS-HP-04 (Shimla)", "AWS-RJ-09 (Jodhpur)"]
    )

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("▶️ Start Stream", use_container_width=True):
        st.session_state.running = True
    if col_btn2.button("⏸️ Pause", use_container_width=True):
        st.session_state.running = False

    st.divider()
    st.subheader("🧪 Live Anomaly Injector")
    st.caption("Inject synthetic sensor faults or real storm fronts to test classification:")

    fault_choice = st.radio(
        "Next Frame Scenario:",
        [
            "Normal Telemetry",
            "Inject: Temp Sensor Spike (+20°C)",
            "Inject: Frozen Bus (Stuck Values)",
            "Inject: Dew Point Violation",
            "Simulate: Genuine Storm Front (Valid)"
        ]
    )
    if st.button("⚡ Trigger Scenario Now", type="primary", use_container_width=True):
        st.session_state.inject_fault = fault_choice

    st.divider()
    if st.button("🔄 Reset Telemetry Buffer", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def get_next_frame():
    i = st.session_state.step
    st.session_state.step += 1
    scenario = st.session_state.inject_fault
    st.session_state.inject_fault = "None"

    base_t = 24.0 + 4.0 * np.sin(i / 15.0) + np.random.normal(0, 0.15)
    base_p = 1013.0 + 1.5 * np.cos(i / 20.0) + np.random.normal(0, 0.2)
    base_h = 62.0 - 8.0 * np.sin(i / 15.0) + np.random.normal(0, 0.5)

    if scenario == "Inject: Temp Sensor Spike (+20°C)":
        return {'temperature': round(base_t + 20.0, 2), 'pressure': round(base_p, 2), 'humidity': round(base_h, 2)}
    elif scenario == "Inject: Frozen Bus (Stuck Values)":
        last = st.session_state.detector.history[-1]
        st.session_state.detector.history[-2] = last.copy()
        st.session_state.detector.history[-1] = last.copy()
        return last.copy()
    elif scenario == "Inject: Dew Point Violation":
        return {'temperature': 6.0, 'pressure': round(base_p, 2), 'humidity': 99.0}
    elif scenario == "Simulate: Genuine Storm Front (Valid)":
        last = st.session_state.detector.history[-1]
        return {
            'temperature': round(last['temperature'] - 0.8, 2),
            'pressure': round(last['pressure'] - 0.9, 2),
            'humidity': round(min(96.0, last['humidity'] + 3.5), 2)
        }
    else:
        return {'temperature': round(base_t, 2), 'pressure': round(base_p, 2), 'humidity': round(base_h, 2)}


if st.session_state.running or st.session_state.inject_fault != "None":
    reading = get_next_frame()
    is_anom, sev, conf, cause, xai_reason, imputed = st.session_state.detector.process_realtime_reading(reading)

    record = {
        "Timestamp": pd.Timestamp.now().strftime("%H:%M:%S"),
        "Raw_Temp": reading['temperature'],
        "Raw_Pres": reading['pressure'],
        "Raw_Hum": reading['humidity'],
        "Healed_Temp": imputed['temperature'],
        "Healed_Pres": imputed['pressure'],
        "Healed_Hum": imputed['humidity'],
        "Anomaly": is_anom,
        "Severity": sev,
        "Confidence": conf,
        "Root_Cause": cause,
        "XAI_Explanation": xai_reason
    }
    st.session_state.stream_log.append(record)
    if len(st.session_state.stream_log) > 50:
        st.session_state.stream_log.pop(0)

    if is_anom:
        st.session_state.alert_log.insert(0, record)

# Main Dashboard UI
st.title("🌦️ Intelligent AWS Real-Time Anomaly & Health Monitor")
st.caption(f"Active Node: **{station_id}** | Edge-Cloud Hybrid Engine (Isolation Forest + Thermodynamic Consistency)")

det = st.session_state.detector
health_score = max(0.0, round(100.0 - (det.fault_count / max(1, det.total_frames)) * 100.0, 1))

k1, k2, k3, k4 = st.columns(4)
latest = st.session_state.stream_log[-1] if st.session_state.stream_log else {
    "Raw_Temp": 24.0, "Raw_Pres": 1013.0, "Raw_Hum": 62.0, "Anomaly": False
}

k1.metric("🌡️ Temperature", f"{latest['Raw_Temp']} °C", delta=f"Healed: {latest.get('Healed_Temp')} °C" if latest['Anomaly'] else "Verified")
k2.metric("⏲️ Pressure", f"{latest['Raw_Pres']} hPa", delta=f"Healed: {latest.get('Healed_Pres')} hPa" if latest['Anomaly'] else "Verified")
k3.metric("💧 Rel. Humidity", f"{latest['Raw_Hum']} %", delta=f"Healed: {latest.get('Healed_Hum')} %" if latest['Anomaly'] else "Verified")
k4.metric("🩺 Sensor Health Index", f"{health_score}%", delta="Maintenance Needed" if health_score < 85 else "Optimal", delta_color="normal" if health_score >= 85 else "inverse")

if st.session_state.stream_log:
    if latest["Anomaly"]:
        st.error(
            f"🚨 **ANOMALY DETECTED [{latest['Root_Cause']}]** — Severity: **{latest['Severity']}** | "
            f"Confidence: **{int(latest['Confidence']*100)}%**

"
            f"💡 **XAI Reasoning:** {latest['XAI_Explanation']} | "
            f"🛠️ **Auto-Imputed:** T={latest['Healed_Temp']}°C, P={latest['Healed_Pres']}hPa, H={latest['Healed_Hum']}%"
        )
    else:
        st.success(f"✅ **STATUS NOMINAL** — {latest['XAI_Explanation']} (Confidence: {int(latest['Confidence']*100)}%)")

if st.session_state.stream_log:
    df_stream = pd.DataFrame(st.session_state.stream_log)

    c1, c2 = st.columns(2)
    with c1:
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(x=df_stream["Timestamp"], y=df_stream["Raw_Temp"], mode='lines+markers', name='Raw Sensor (°C)', line=dict(color='#FF6B6B')))
        fig_t.add_trace(go.Scatter(x=df_stream["Timestamp"], y=df_stream["Healed_Temp"], mode='lines', name='Imputed / Clean (°C)', line=dict(color='#4ECDC4', dash='dash')))
        fig_t.update_layout(title="Temperature Stream vs. Self-Healed Baseline", height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_t, use_container_width=True)

    with c2:
        fig_ph = go.Figure()
        fig_ph.add_trace(go.Scatter(x=df_stream["Timestamp"], y=df_stream["Raw_Pres"], mode='lines', name='Pressure (hPa)', line=dict(color='#FFD166')))
        fig_ph.add_trace(go.Scatter(x=df_stream["Timestamp"], y=df_stream["Raw_Hum"], mode='lines', name='Humidity (%)', yaxis='y2', line=dict(color='#118AB2')))
        fig_ph.update_layout(
            title="Multivariate Coupling: Pressure vs. Humidity",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            yaxis=dict(title="hPa"),
            yaxis2=dict(title="%", overlaying='y', side='right')
        )
        st.plotly_chart(fig_ph, use_container_width=True)

st.subheader("📋 Explainable Anomaly Audit Log")
if st.session_state.alert_log:
    df_alerts = pd.DataFrame(st.session_state.alert_log)[
        ["Timestamp", "Root_Cause", "Severity", "Confidence", "Raw_Temp", "Healed_Temp", "XAI_Explanation"]
    ]
    st.dataframe(df_alerts, use_container_width=True, hide_index=True)
else:
    st.info("No anomalies flagged yet. Click **Start Stream** or use the **Live Anomaly Injector** in the sidebar to test detection.")

if st.session_state.running:
    time.sleep(1.0)
    st.rerun()
