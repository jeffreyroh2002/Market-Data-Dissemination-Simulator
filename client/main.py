"""
client/main.py
Subscribe to two instruments (ES, AAPL) and print live book updates.
Run with:  python -m client.main
"""

import grpc
import market_data_pb2
import market_data_pb2_grpc


def run() -> None:
    channel = grpc.insecure_channel("localhost:50051")

    # Wait until channel ready (optional safety)
    try:
        grpc.channel_ready_future(channel).result(timeout=5)
        print("✅ connected to server")
    except grpc.FutureTimeoutError:
        print("❌ server not reachable")
        return

    stub = market_data_pb2_grpc.MarketDataStub(channel)

    # ── the generator that sends multiple SubscribeRequest messages ──
    def gen():
        yield market_data_pb2.SubscribeRequest(instrument_id="ES")
        yield market_data_pb2.SubscribeRequest(instrument_id="AAPL")
        # you could keep yielding more SubscribeRequest objects later
        # (e.g. driven by user input) if you want dynamic subscriptions

    # receive snapshot + incremental updates for every subscribed instrument
    for upd in stub.Subscribe(gen()):
        print(
            f"\n{upd.update_type.upper():<11} {upd.instrument_id}\n"
            f"Bids: {upd.updated_bids}\n"
            f"Asks: {upd.updated_asks}"
        )


if __name__ == "__main__":
    run()