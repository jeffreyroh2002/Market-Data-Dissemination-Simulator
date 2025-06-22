# Architecture Overview — Market Data Dissemination Simulator

## System Components

### Config Loader (`server/config_loader.py`)

- Reads the instrument configuration from `instruments.json`
- Defines order book depth per instrument


### Order Book (`server/order_book.py`)

- Simulates a single instrument’s order book state
- Generates:
  - Full snapshots (`get_snapshot()`)
  - Randomized incremental updates (`generate_update()`)


### Order Book Manager (`server/order_book_manager.py`)

- Manages multiple `OrderBook` instances across all configured instruments
- Provides access to snapshots and updates for each instrument


### Server (`server/main.py`)

- Implements gRPC server using `market_data.proto`
- Accepts client subscriptions for instruments
- Streams:
  - Initial snapshot upon subscription
  - Continuous incremental updates via bidirectional gRPC streaming


### Client (`client/main.py`)

- gRPC client that:
  - Submits subscription requests for specific instruments
  - Receives real-time snapshots and incremental updates
  - Continuously processes incoming order book data


### Protobuf Interface (`proto/market_data.proto`)

- Defines the message schema for:
  - `SubscribeRequest`
  - `OrderBookUpdate`
- Defines gRPC service:
  - `MarketData.Subscribe()` — bidirectional streaming RPC

## Data Flow

1. **Config Load** → `OrderBookManager` initializes `OrderBook` instances from `instruments.json`
2. **Client Connects** → Sends `SubscribeRequest` via gRPC stream
3. **Server Streams Data**:
   - Sends full snapshot (`OrderBookUpdate` with type `snapshot`)
   - Continues sending live incremental updates (`update_type: incremental`)
4. **Client Receives Data** → Prints updates, maintains synchronized order book state
