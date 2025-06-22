# server/main.py
# gRPC server that streams snapshots + incremental order-book updates

import grpc
from concurrent import futures
import time, random

import market_data_pb2
import market_data_pb2_grpc

from server.order_book_manager import OrderBookManager

CONFIG_PATH = "config/instruments.json"
manager = OrderBookManager(CONFIG_PATH)


class MarketDataService(market_data_pb2_grpc.MarketDataServicer):
    def Subscribe(self, request_iterator, context):
        print("client connected")
        subscribed = set()

        for req in request_iterator:
            ins = req.instrument_id
            if ins not in subscribed:
                subscribed.add(ins)
                bids, asks = manager.get_snapshot(ins)
                yield market_data_pb2.OrderBookUpdate(
                    instrument_id=ins,
                    updated_bids=bids,
                    updated_asks=asks,
                    update_type="snapshot"
                )

            # continuous incremental stream
            while True:
                bids, asks, _ = manager.generate_update(ins)
                yield market_data_pb2.OrderBookUpdate(
                    instrument_id=ins,
                    updated_bids=bids,
                    updated_asks=asks,
                    update_type="incremental"
                )
                time.sleep(random.uniform(0.5, 1.5))


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    market_data_pb2_grpc.add_MarketDataServicer_to_server(
        MarketDataService(), server
    )
    server.add_insecure_port("[::]:50051")
    print("server listening on :50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()