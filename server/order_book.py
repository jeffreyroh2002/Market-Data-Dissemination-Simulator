# server/order_book.py

import random

class OrderBook:
    def __init__(self, instrument_id, depth):
        self.instrument_id = instrument_id
        self.depth = depth
        self.bids = []
        self.asks = []
        self._initialize_book()

    def _initialize_book(self):
        """Initialize with random prices for simulation"""
        mid_price = 100.0  # starting mid-price for simulation
        spread = 0.5
        for i in range(self.depth):
            bid_price = mid_price - spread - i * 0.1
            ask_price = mid_price + spread + i * 0.1
            self.bids.append((bid_price, random.randint(1, 10)))  # (price, size)
            self.asks.append((ask_price, random.randint(1, 10)))

    def get_snapshot(self):
        """Return current full snapshot"""
        bids = [price for price, size in self.bids]
        asks = [price for price, size in self.asks]
        return bids, asks

    def generate_update(self):
        """Simulate an update (random price change)"""
        # Randomly pick bid or ask to update
        side = random.choice(['bid', 'ask'])
        index = random.randint(0, self.depth - 1)

        if side == 'bid':
            price, size = self.bids[index]
            delta = random.uniform(-0.05, 0.05)
            self.bids[index] = (price + delta, size)
        else:
            price, size = self.asks[index]
            delta = random.uniform(-0.05, 0.05)
            self.asks[index] = (price + delta, size)

        bids = [price for price, size in self.bids]
        asks = [price for price, size in self.asks]
        return bids, asks, side  # returning side just for testing now
