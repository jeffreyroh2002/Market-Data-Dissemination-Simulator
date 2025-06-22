import time
import grpc

import market_data_pb2
import market_data_pb2_grpc


def run() -> None:
    # 1. Create channel to gRPC server
    channel = grpc.insecure_channel("localhost:50051")

    # 2. Wait (up to 5 s) for channel to become ready
    try:
        grpc.channel_ready_future(channel).result(timeout=5)
        print("✅ connected to server on localhost:50051")
    except grpc.FutureTimeoutError:
        print("❌ server not reachable on localhost:50051 (is it running?)")
        return

    # 3. Create a stub
    stub = market_data_pb2_grpc.MarketDataStub(channel)

    # 4. Generator that sends our subscription request(s)
    def request_stream():
        yield market_data_pb2.SubscribeRequest(instrument_id="ES")

    # 5. Receive snapshot + incremental updates
    for update in stub.Subscribe(request_stream()):
        print(
            f"\n{update.update_type.upper():<11} {update.instrument_id}\n"
            f"Bids: {update.updated_bids}\n"
            f"Asks: {update.updated_asks}"
        )
        # (Optional) small pause to make console output readable
        time.sleep(0.1)

if __name__ == "__main__":
    run()
