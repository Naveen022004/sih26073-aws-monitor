import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


class AWSIntelligentDetector:
    """
    Hybrid AI + Thermodynamic Anomaly Detection Engine for Automatic Weather Stations (SIH26073).
    Monitors Temperature (°C), Atmospheric Pressure (hPa), and Relative Humidity (%).
    """

    def __init__(self, window_size=30, contamination=0.05):
        self.window_size = window_size
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.history = []
        self.is_trained = False
        self.fault_count = 0
        self.total_frames = 0

        self.PHYSICAL_LIMITS = {
            'temperature': (-10.0, 55.0),
            'pressure': (900.0, 1050.0),
            'humidity': (0.0, 100.0)
        }
        self.MAX_RATE_OF_CHANGE = {
            'temperature': 3.0,
            'pressure': 2.0,
            'humidity': 10.0
        }

    def compute_dew_point(self, temp, humidity):
        """Magnus-Tetens formula to compute Dew Point (°C) for thermodynamic cross-validation."""
        a, b = 17.27, 237.7
        alpha = ((a * temp) / (b + temp)) + np.log(max(humidity, 0.1) / 100.0)
        return (b * alpha) / (a - alpha)

    def fit_baseline(self, historical_data):
        """Trains the Isolation Forest model on normal diurnal/seasonal weather observations."""
        df = pd.DataFrame(historical_data)
        self.model.fit(df[['temperature', 'pressure', 'humidity']])
        self.is_trained = True
        self.history = [row.copy() for row in historical_data[-self.window_size:]]

    def process_realtime_reading(self, current_reading):
        """
        Evaluates a single streaming telemetry frame.
        Returns: (is_anomaly, severity, confidence, root_cause, explanation, imputed_dict)
        """
        self.total_frames += 1
        t = float(current_reading['temperature'])
        p = float(current_reading['pressure'])
        h = float(current_reading['humidity'])

        is_anomaly = False
        severity = 0.0
        confidence = 0.98
        root_cause = "Nominal Operation"
        explanation = "All parameters align with diurnal cycles and thermodynamic laws."
        imputed = {'temperature': t, 'pressure': p, 'humidity': h}

        # Stage 1: Hard Physical Limits
        for param, (low, high) in self.PHYSICAL_LIMITS.items():
            val = float(current_reading[param])
            if val < low or val > high:
                self.fault_count += 1
                return (
                    True,
                    1.0,
                    0.99,
                    "Hard Boundary Fault",
                    f"{param.capitalize()} ({val}) exceeded physical sensor bounds [{low}, {high}].",
                    self._impute(param),
                )

        # Stage 2: Temporal Rate-of-Change & Frozen Sensor Check
        if len(self.history) >= 3:
            hist_df = pd.DataFrame(self.history)
            last = self.history[-1]

            if all(
                np.allclose(hist_df[col].iloc[-3:], float(current_reading[col]), atol=1e-4)
                for col in ['temperature', 'pressure', 'humidity']
            ):
                self.fault_count += 1
                return (
                    True,
                    0.85,
                    0.95,
                    "Frozen Sensor / Comm Lock",
                    "Zero variance across 3 consecutive frames; sensor bus likely hung.",
                    self._impute(None),
                )

            for param in ['temperature', 'pressure', 'humidity']:
                delta = abs(float(current_reading[param]) - float(last[param]))
                if delta > self.MAX_RATE_OF_CHANGE[param]:
                    self.fault_count += 1
                    sev = min(1.0, round(delta / (self.MAX_RATE_OF_CHANGE[param] * 2), 2))
                    return (
                        True,
                        sev,
                        0.94,
                        "Non-Meteorological Spike",
                        f"Sudden jump of {delta:.2f} in {param} violates atmospheric inertia.",
                        self._impute(param),
                    )

        # Stage 3: Multivariate ML + Thermodynamic Consistency Check
        if self.is_trained:
            features = pd.DataFrame([[t, p, h]], columns=['temperature', 'pressure', 'humidity'])
            pred = self.model.predict(features)[0]
            score = float(-self.model.score_samples(features)[0])
            dp = self.compute_dew_point(t, h)

            if t < dp - 0.5:
                self.fault_count += 1
                return (
                    True,
                    0.90,
                    0.96,
                    "Thermodynamic Inconsistency",
                    f"Temp ({t:.1f}°C) fell below Dew Point ({dp:.1f}°C) without saturation balance.",
                    self._impute(None),
                )
            elif pred == -1:
                self.fault_count += 1
                sev = float(np.clip(round(score * 1.5, 2), 0.45, 0.92))
                return (
                    True,
                    sev,
                    0.88,
                    "Multivariate Drift",
                    "Joint distribution of T-P-H deviates from learned seasonal baseline.",
                    self._impute(None),
                )

        self.history.append({'temperature': t, 'pressure': p, 'humidity': h})
        if len(self.history) > self.window_size:
            self.history.pop(0)

        return is_anomaly, severity, confidence, root_cause, explanation, imputed

    def _impute(self, target_param):
        """Self-healing data estimation using rolling window median."""
        if not self.history:
            return {'temperature': 24.0, 'pressure': 1013.0, 'humidity': 60.0}
        hist_df = pd.DataFrame(self.history)
        imputed = {}
        for param in ['temperature', 'pressure', 'humidity']:
            if param == target_param or target_param is None:
                imputed[param] = round(float(hist_df[param].median()), 2)
            else:
                imputed[param] = round(float(hist_df[param].iloc[-1]), 2)
        return imputed
