# client/main.py

import grpc
import time

import sys
sys.path.append('../server')  # so we can import generated proto files

import market_data_pb2
import market_data_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = market_data_pb2_grpc.MarketDataStub(channel)

    def request_generator():
        # Subscribe to ES instrument
        yield market_data_pb2.SubscribeRequest(instrument_id="ES")

    responses = stub.Subscribe(request_generator())

    for response in responses:
        print(f"\nReceived update for instrument: {response.instrument_id}")
        print(f"Bids: {response.updated_bids}")
        print(f"Asks: {response.updated_asks}")
        print(f"Update Type: {response.update_type}")

if __name__ == '__main__':
    run()
