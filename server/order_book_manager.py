# server/order_book_manager.py

from server.order_book import OrderBook
from server.config_loader import load_config
from collections import deque

class OrderBookManager:
    def __init__(self, config_path):
        self.configs = load_config(config_path)
        self.books = {}
        self._initialize_books()
        self.buffers = {ins: deque(maxlen=5_000) for ins in self.books}

    def _initialize_books(self):
        for instrument_id, config in self.configs.items():
            self.books[instrument_id] = OrderBook(
                instrument_id=instrument_id,
                depth=config.order_book_depth
            )

    def get_snapshot(self, instrument_id):
        if instrument_id not in self.books:
            raise ValueError(f"Instrument {instrument_id} not found")
        return self.books[instrument_id].get_snapshot()
    
    def generate_update(self, instrument_id):
        seq, bids, asks, ev = self.books[instrument_id].generate_update()
        upd = {
            "seq": seq,
            "bids": bids,
            "asks": asks,
            "type": ev,
        }
        self.buffers[instrument_id].append(upd)
        return upd
