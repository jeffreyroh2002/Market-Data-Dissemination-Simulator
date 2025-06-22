# server/main.py

import grpc
from concurrent import futures
import time
import random

import market_data_pb2
import market_data_pb2_grpc

from order_book_manager import OrderBookManager

# Load configs
CONFIG_PATH = "../config/instruments.json"
manager = OrderBookManager(CONFIG_PATH)

class MarketDataService(market_data_pb2_grpc.MarketDataServicer):
    def Subscribe(self, request_iterator, context):
        print("Client connected.")

        # Keep track of instruments this client subscribes to
        subscribed_instruments = set()

        for request in request_iterator:
            instrument_id = request.instrument_id

            # Handle new subscription
            if instrument_id not in subscribed_instruments:
                subscribed_instruments.add(instrument_id)
                print(f"Subscribed to instrument: {instrument_id}")

                # Send initial snapshot
                bids, asks = manager.get_snapshot(instrument_id)
                snapshot = market_data_pb2.OrderBookUpdate(
                    instrument_id=instrument_id,
                    updated_bids=bids,
                    updated_asks=asks,
                    update_type="snapshot"
                )
                yield snapshot

            # After initial subscription, keep sending simulated updates
            # (Note: in real life you'd run async background updates)
            for _ in range(5):  # simulate 5 incremental updates
                bids, asks, _ = manager.generate_update(instrument_id)
                update = market_data_pb2.OrderBookUpdate(
                    instrument_id=instrument_id,
                    updated_bids=bids,
                    updated_asks=asks,
                    update_type="incremental"
                )
                time.sleep(random.uniform(0.5, 1.5))
                yield update

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    market_data_pb2_grpc.add_MarketDataServicer_to_server(MarketDataService(), server)
    server.add_insecure_port('[::]:50051')
    print("Starting server on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()