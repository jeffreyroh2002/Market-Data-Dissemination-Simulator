# benchmark/plot_latency.py

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(
    "benchmark_results.csv",
    names=["timestamp", "instrument", "seq_no", "latency_ms"],
    skiprows=1,
)

# normalize time to start at zero
df["time_offset_s"] = df["timestamp"] - df["timestamp"].iloc[0]

plt.figure(figsize=(10, 6))

for ins in df["instrument"].unique():
    subset = df[df["instrument"] == ins]
    plt.plot(
        subset["time_offset_s"],
        subset["latency_ms"],
        label=ins,
        alpha=0.7,
    )

plt.title("Per-instrument Latency Over Time")
plt.xlabel("Time since start (s)")
plt.ylabel("Latency (ms)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("latency_plot.png")
plt.show()
