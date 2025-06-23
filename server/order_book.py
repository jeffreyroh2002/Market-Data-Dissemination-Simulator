from dataclasses import dataclass
import random, itertools

@dataclass
class BookLevel:
    price: float
    size: int     # 0 => empty

class OrderBook:
    _seq = itertools.count()          # global monotonic sequence

    def __init__(self, instrument_id: str, depth: int):
        self.instrument_id = instrument_id
        self.depth = depth
        self.bids: list[BookLevel] = []
        self.asks: list[BookLevel] = []
        self._init_book()

    def _init_book(self) -> None:
        mid = 100.0
        spread = 0.5
        for i in range(self.depth):
            self.bids.append(BookLevel(mid - spread - i*0.1, random.randint(5,15)))
            self.asks.append(BookLevel(mid + spread + i*0.1, random.randint(5,15)))

    # ──────────────────────────────────────────────────────────────
    def snapshot_prices(self):
        """Return only price lists (sizes optional for v-1)."""
        return ([lvl.price for lvl in self.bids],
                [lvl.price for lvl in self.asks])

    # simple wrapper so existing code continues to work
    def get_snapshot(self):
        return self.snapshot_prices()

    def generate_update(self):
        """Produce one random micro-event and return new price lists."""
        side = random.choice(["bid","ask"])
        book = self.bids if side=="bid" else self.asks
        lvl   = random.randint(0, self.depth-1)
        event = random.choices(
            ["modify", "cancel", "partial"],
            weights=[0.5, 0.25, 0.25]
        )[0]

        level = book[lvl]

        if event == "modify":
            level.price = round(level.price + random.uniform(-0.05,0.05), 2)

        elif event == "cancel":
            level.size = 0                # mark empty

        elif event == "partial":
            if level.size <= 1:
                # size 1 (or 0)  ⇒ treat as full cancel
                level.size = 0
                event = "cancel"
            else:
                fill = random.randint(1, level.size - 1)   # leave at least 1
                level.size -= fill

        # prune cancels (size==0) then pad depth
        if level.size == 0:
            del book[lvl]
            pad_price = (book[0].price - 0.01) if side=="bid" else (book[-1].price + 0.01)
            book.append(BookLevel(pad_price, 0))

        seq_no = next(OrderBook._seq)
        bids, asks = self.snapshot_prices()
        return seq_no, bids, asks, event
