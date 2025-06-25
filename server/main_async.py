import asyncio
import time
import random
import grpc
import market_data_pb2 as pb
import market_data_pb2_grpc as pb_grpc

from server.order_book_manager import OrderBookManager

CONFIG_PATH = "config/instruments.json"
manager = OrderBookManager(CONFIG_PATH)

class MDService(pb_grpc.MarketDataServicer):
    def __init__(self):
        self.subs = {}
        self.queues = {}
        self.buffers = manager.buffers
        self.ins_profile = manager.ins_profile
        self.profiles = manager.profiles

    async def _enqueue_snapshot(self, q, ins):
        bids, asks = manager.books[ins].snapshot_prices()
        await q.put(
            pb.OrderBookUpdate(
                seq_no=0,
                instrument_id=ins,
                updated_bids=bids,
                updated_asks=asks,
                update_type="snapshot",
                send_ts_ns=time.time_ns()
            )
        )

    async def _replay(self, q, ins, last_seq):
        buf = self.buffers[ins]
        if not buf or buf[-1]["seq"] - last_seq > len(buf):
            await self._enqueue_snapshot(q, ins)
            return

        for d in buf:
            if d["seq"] > last_seq:
                await q.put(
                    pb.OrderBookUpdate(
                        seq_no=d["seq"],
                        instrument_id=ins,
                        updated_bids=d["bids"],
                        updated_asks=d["asks"],
                        update_type=d["type"],
                        send_ts_ns=time.time_ns()
                    )
                )

    async def Subscribe(self, request_iterator, context):
        ctx = context
        self.subs[ctx] = set()
        self.queues[ctx] = asyncio.Queue()

        async def read_requests():
            async for req in request_iterator:
                ins, last_seq = req.instrument_id, req.last_seq
                if ins not in manager.books:
                    continue
                if ins not in self.subs[ctx]:
                    self.subs[ctx].add(ins)
                    if last_seq == 0:
                        await self._enqueue_snapshot(self.queues[ctx], ins)
                    else:
                        await self._replay(self.queues[ctx], ins, last_seq)

        asyncio.create_task(read_requests())

        try:
            while True:
                upd = await self.queues[ctx].get()
                yield upd
        except asyncio.CancelledError:
            pass
        finally:
            self.subs.pop(ctx, None)
            self.queues.pop(ctx, None)

    async def publisher_loop(self):
        while True:
            await asyncio.sleep(0.5)
            for ins in manager.books:
                delta = manager.generate_update(ins)
                self.buffers[ins].append(delta)

                profile = self.ins_profile[ins]
                cfg = self.profiles[profile]
                await asyncio.sleep(random.expovariate(cfg["event_rate_hz"]))
                await asyncio.sleep(random.gauss(cfg["latency_mean_ms"], cfg["latency_jitter_ms"]) / 1000.0)

                upd = pb.OrderBookUpdate(
                    seq_no=delta["seq"],
                    instrument_id=ins,
                    updated_bids=delta["bids"],
                    updated_asks=delta["asks"],
                    update_type=delta["type"],
                    send_ts_ns=time.time_ns()
                )

                for ctx, instruments in list(self.subs.items()):
                    if ins in instruments and not ctx.done():
                        await self.queues[ctx].put(upd)

async def serve_async():
    svc = MDService()
    server = grpc.aio.server()
    pb_grpc.add_MarketDataServicer_to_server(svc, server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    print("async server on :50051")

    asyncio.create_task(svc.publisher_loop())
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve_async())
