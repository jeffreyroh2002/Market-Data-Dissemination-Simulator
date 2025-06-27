# client/main.py

import grpc
import time
from collections import defaultdict
from statistics import mean
from proto import market_data_pb2 as pb
from proto import market_data_pb2_grpc as pb_grpc

latencies = defaultdict(list)
counts = defaultdict(int)
start = time.time()


def gen():
    yield pb.SubscribeRequest(instrument_id="ES")
    yield pb.SubscribeRequest(instrument_id="AAPL")


def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = pb_grpc.MarketDataStub(channel)

    print("\u2705 connected to server")

    for upd in stub.Subscribe(gen()):
        now = time.time()
        latency_ms = (now * 1e9 - upd.send_ts_ns) / 1e6

        latencies[upd.instrument_id].append(latency_ms)
        counts[upd.instrument_id] += 1

        print(
            f"{upd.instrument_id:5} {upd.update_type:8}  seq={upd.seq_no:<5}  latency={latency_ms:.3f} ms"
        )

        # every 50 updates per instrument, print basic stats
        if counts[upd.instrument_id] % 50 == 0:
            l = latencies[upd.instrument_id]
            print(
                f"\n--- {upd.instrument_id} STATS ---\n"
                f"received: {len(l)}\n"
                f"mean latency: {mean(l):.2f} ms\n"
                f"p95 latency: {sorted(l)[int(0.95 * len(l))]:.2f} ms\n"
                f"p99 latency: {sorted(l)[int(0.99 * len(l)) - 1]:.2f} ms\n"
            )


if __name__ == "__main__":
    run()
