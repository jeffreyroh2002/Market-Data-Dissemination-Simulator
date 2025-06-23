from server.order_book import OrderBook

def test_cancel_level_removed():
    ob = OrderBook("TEST", 3)
    ob.bids[1].size = 1           # will be fully filled

    import random
    random.choice  = lambda _: "bid"        # always bid side
    random.randint = lambda a, b: 1         # idx = 1 and fill = 1
    random.choices = lambda *_, **__: ["partial"]

    seq, bids, asks, ev = ob.generate_update()

    assert ev == "cancel"
    # exactly one padded bid level has size 0 after pruning
    zero_sizes = [lvl.size for lvl in ob.bids].count(0)
    assert zero_sizes == 1
    assert len(ob.bids) == 3                # depth preserved
