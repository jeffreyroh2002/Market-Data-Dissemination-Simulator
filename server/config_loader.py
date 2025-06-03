# server/config_loader.py

import json

class InstrumentConfig:
    def __init__(self, instrument_id, order_book_depth):
        self.instrument_id = instrument_id
        self.order_book_depth = order_book_depth

    def __repr__(self):
        return f"<InstrumentConfig id={self.instrument_id}, depth={self.order_book_depth}>"

def load_config(path: str):
    with open(path, "r") as f:
        raw_data = json.load(f)

    configs = {}
    for item in raw_data.get("instruments", []):
        instrument_id = item["instrument_id"]
        depth = item["order_book_depth"]
        configs[instrument_id] = InstrumentConfig(instrument_id, depth)

    return configs