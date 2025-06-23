import asyncio, random, grpc
import market_data_pb2, market_data_pb2_grpc
from server.order_book_manager import OrderBookManager

CONFIG_PATH = "config/instruments.json"
manager = OrderBookManager(CONFIG_PATH)


class MDService(market_data_pb2_grpc.MarketDataServicer):
    def __init__(self):
        self.subs   = {}   # ctx -> set[instruments]
        self.queues = {}   # ctx -> asyncio.Queue

    async def Subscribe(self, request_iterator, context):
        self.subs[context]   = set()
        self.queues[context] = asyncio.Queue()

        async for req in request_iterator:
            ins = req.instrument_id
            if ins not in self.subs[context]:
                self.subs[context].add(ins)
                bids, asks = manager.get_snapshot(ins)
                await self.queues[context].put(
                    market_data_pb2.OrderBookUpdate(
                        instrument_id=ins,
                        updated_bids=bids,
                        updated_asks=asks,
                        update_type="snapshot",
                    )
                )

        # streaming response
        try:
            while True:
                upd = await self.queues[context].get()
                yield upd
        finally:
            self.subs.pop(context, None)
            self.queues.pop(context, None)

    # background task
    async def publisher_loop(self):
        while True:
            await asyncio.sleep(0.5)
            for ins in manager.configs.keys():
                seq, bids, asks, ev = manager.generate_update(ins)
                upd = market_data_pb2.OrderBookUpdate(
                    instrument_id=ins,
                    updated_bids=bids,
                    updated_asks=asks,
                    update_type=ev,
                )
                for ctx, instruments in list(self.subs.items()):
                    # ctx.done() returns an asyncio.Future that completes when the stream is closed
                    if ins in instruments and not ctx.done():
                        await self.queues[ctx].put(upd)


async def serve():
    svc = MDService()
    server = grpc.aio.server()
    market_data_pb2_grpc.add_MarketDataServicer_to_server(svc, server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    print("async server on :50051")
    # launch background publisher
    asyncio.create_task(svc.publisher_loop())
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())