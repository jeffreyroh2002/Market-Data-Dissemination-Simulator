import json
from collections import deque
from server.order_book import OrderBook

class OrderBookManager:
    def __init__(self, config_path):
        with open(config_path) as f:
            data = json.load(f)

        self.profiles = data["profiles"]
        self.default_profile = data["default_profile"]

        self.books = {}
        self.ins_profile = {}
        for ins_cfg in data["instruments"]:
            ins_id = ins_cfg["instrument_id"]
            depth = ins_cfg["order_book_depth"]
            profile = ins_cfg.get("profile", self.default_profile)
            self.books[ins_id] = OrderBook(ins_id, depth)
            self.ins_profile[ins_id] = profile

        self.buffers = {ins: deque(maxlen=5000) for ins in self.books}

    def generate_update(self, instrument_id):
        delta = self.books[instrument_id].generate_update()
        self.buffers[instrument_id].append(delta)
        return delta
