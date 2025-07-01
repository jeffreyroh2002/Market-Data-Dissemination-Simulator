import asyncio
import websockets
import json

async def binance_order_book():
    uri = "wss://stream.binance.com:9443/ws/btcusdt@depth5@100ms"
    async with websockets.connect(uri) as websocket:
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            bids = data["bids"]
            asks = data["asks"]
            print(f"Bids: {bids}")
            print(f"Asks: {asks}")

asyncio.run(binance_order_book())