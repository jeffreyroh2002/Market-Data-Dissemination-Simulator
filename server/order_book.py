import random
import itertools
from dataclasses import dataclass

@dataclass
class BookLevel:
    price: float
    size: int

class OrderBook:
    _seq = itertools.count()

    def __init__(self, instrument_id, depth):
        self.instrument_id = instrument_id
        self.depth = depth
        self.bids = [BookLevel(price=100 - i * 0.1, size=10) for i in range(depth)]
        self.asks = [BookLevel(price=100 + i * 0.1, size=10) for i in range(depth)]

    def snapshot_prices(self):
        return ([lvl.price for lvl in self.bids],
                [lvl.price for lvl in self.asks])

    def get_snapshot(self):
        return self.snapshot_prices()

    def generate_update(self):
        side = random.choice(["bid", "ask"])
        book = self.bids if side == "bid" else self.asks
        idx = random.randint(0, self.depth - 1)

        event = random.choices(
            ["modify", "partial", "cancel"],
            weights=[0.5, 0.3, 0.2]
        )[0]

        if event == "modify":
            delta = random.uniform(-0.02, 0.02)
            book[idx].price += delta

        elif event == "partial":
            reduction = random.randint(1, max(1, book[idx].size // 2))
            book[idx].size -= reduction
            if book[idx].size <= 0:
                book.pop(idx)
                book.append(BookLevel(price=book[-1].price - 0.1 if side == "bid" else book[-1].price + 0.1, size=10))

        elif event == "cancel":
            book.pop(idx)
            book.append(BookLevel(price=book[-1].price - 0.1 if side == "bid" else book[-1].price + 0.1, size=10))

        seq = next(OrderBook._seq)
        return {
            "seq": seq,
            "bids": [lvl.price for lvl in self.bids],
            "asks": [lvl.price for lvl in self.asks],
            "type": event
        }
