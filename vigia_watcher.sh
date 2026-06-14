#!/usr/bin/env python3

import csv
import time
import statistics
from collections import deque
from pathlib import Path

WINDOW = 50
THRESHOLD_Z = 3.0

class TemporalAnomalyDetector:
    def __init__(self):
        self.window = deque(maxlen=WINDOW)

    def update(self, value):
        self.window.append(value)

        if len(self.window) < 10:
            return None

        mean = statistics.mean(self.window)
        stdev = statistics.stdev(self.window)

        if stdev == 0:
            return None

        z = abs((value - mean) / stdev)

        return {
            "value": value,
            "mean": mean,
            "stdev": stdev,
            "zscore": z,
            "anomaly": z > THRESHOLD_Z
        }

def tail_sensor_file(filepath):
    detector = TemporalAnomalyDetector()

    print("=" * 60)
    print("VIGIA TEMPORAL ANOMALY MONITOR")
    print("=" * 60)

    with open(filepath, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            value = float(row["water_level"])

            result = detector.update(value)

            if not result:
                continue

            if result["anomaly"]:
                print(
                    f"[ALERT] "
                    f"value={result['value']:.3f} "
                    f"z={result['zscore']:.2f}"
                )
            else:
                print(
                    f"[OK] "
                    f"value={result['value']:.3f} "
                    f"z={result['zscore']:.2f}"
                )

if __name__ == "__main__":
    tail_sensor_file("sensor_data.csv")
