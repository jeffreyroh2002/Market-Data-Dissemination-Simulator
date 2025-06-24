"""
Client that subscribes to ES and AAPL,
tracks last seq_no, reconnects if connection drops.
Run with:  python -m client.main
"""

import time
import grpc
import market_data_pb2 as pb
import market_data_pb2_grpc as pb_grpc

INSTRUMENTS = ["ES", "AAPL"]


def connect(last_seq_map: dict[str, int]):
    channel = grpc.insecure_channel("localhost:50051")
    stub = pb_grpc.MarketDataStub(channel)

    def gen():
        for ins in INSTRUMENTS:
            last = last_seq_map.get(ins, 0)
            yield pb.SubscribeRequest(instrument_id=ins, last_seq=last)

    return stub.Subscribe(gen())


def main():
    last_seq: dict[str, int] = {}
    while True:
        try:
            for upd in connect(last_seq):
                last_seq[upd.instrument_id] = upd.seq_no
                print(
                    f"{upd.update_type:<10} {upd.instrument_id}  "
                    f"seq={upd.seq_no}  bid0={upd.updated_bids[0]:.2f}"
                )
        except grpc.RpcError as e:
            print(f"stream error ({e.code()}) – reconnecting in 1 s")
            time.sleep(1)


if __name__ == "__main__":
    main()
