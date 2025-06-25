import time
import grpc
import market_data_pb2 as pb
import market_data_pb2_grpc as pb_grpc

INSTRUMENTS = ["ES", "AAPL"]
last_seq = {}

def connect():
    channel = grpc.insecure_channel("localhost:50051")
    stub = pb_grpc.MarketDataStub(channel)

    def gen():
        for ins in INSTRUMENTS:
            yield pb.SubscribeRequest(
                instrument_id=ins,
                last_seq=last_seq.get(ins, 0)
            )
    return stub.Subscribe(gen())

while True:
    try:
        for upd in connect():
            last_seq[upd.instrument_id] = upd.seq_no
            latency_ms = (time.time_ns() - upd.send_ts_ns) / 1e6
            print(f"{upd.instrument_id} {upd.update_type:<10} "
                  f"seq={upd.seq_no:<6} latency={latency_ms:.3f} ms")
    except grpc.RpcError as e:
        print(f"Stream error: {e} — reconnecting")
        time.sleep(1)
