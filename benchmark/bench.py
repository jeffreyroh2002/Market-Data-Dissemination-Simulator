# benchmark/bench.py

import grpc
import time
import csv
import statistics
from collections import defaultdict, deque
from proto import market_data_pb2 as pb
from proto import market_data_pb2_grpc as pb_grpc

INSTRUMENTS = ["ES", "AAPL"]
last_seq = {}
latencies = defaultdict(lambda: deque(maxlen=10000))
counts = defaultdict(int)
start_time = time.time()

csv_file = open("benchmark_results.csv", "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["timestamp", "instrument", "seq_no", "latency_ms"])


def connect():
    channel = grpc.insecure_channel("localhost:50051")
    stub = pb_grpc.MarketDataStub(channel)

    def gen():
        for ins in INSTRUMENTS:
            yield pb.SubscribeRequest(
                instrument_id=ins, last_seq=last_seq.get(ins, 0)
            )
    return stub.Subscribe(gen())


def print_stats():
    elapsed = time.time() - start_time
    print("\n================ BENCHMARK RESULTS ================")
    print(f"Elapsed time: {elapsed:.1f} sec")

    total_msgs = 0
    for ins in INSTRUMENTS:
        lats = list(latencies[ins])
        if not lats:
            continue

        total_msgs += len(lats)
        mean_lat = statistics.mean(lats)
        p50 = statistics.median(lats)
        p95 = sorted(lats)[int(0.95 * len(lats)) - 1]
        p99 = sorted(lats)[int(0.99 * len(lats)) - 1]

        print(
            f"{ins}: msgs={len(lats)}  mean={mean_lat:.3f} ms  "
            f"p50={p50:.3f} ms  p95={p95:.3f} ms  p99={p99:.3f} ms"
        )

    throughput = total_msgs / elapsed
    print(f"Overall throughput: {throughput:.1f} msgs/sec")
    print("===================================================\n")


def run():
    print("✅ benchmark client connected")
    while True:
        try:
            for upd in connect():
                now = time.time()
                last_seq[upd.instrument_id] = upd.seq_no
                latency_ms = (now * 1e9 - upd.send_ts_ns) / 1e6

                latencies[upd.instrument_id].append(latency_ms)
                counts[upd.instrument_id] += 1

                # write to CSV
                csv_writer.writerow([now, upd.instrument_id, upd.seq_no, latency_ms])
                csv_file.flush()

                if int(time.time() - start_time) % 30 == 0:
                    print_stats()

        except grpc.RpcError as e:
            print(f"Stream error: {e} — reconnecting")
            time.sleep(1)


if __name__ == "__main__":
    try:
        run()
    finally:
        csv_file.close()
