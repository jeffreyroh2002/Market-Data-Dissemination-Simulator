# 📡 Market Data Dissemination Simulator

A real-time market data simulator that uses **gRPC** to stream order book snapshots and incremental updates to clients. Designed to mimic real-world trading infrastructure with configurable instruments, order book depth, and a subscription-based update system.

---

## 🚀 Features

- 📘 **Config-driven setup** — Easily define instruments and order book depth via JSON  
- ⚡ **gRPC bidirectional streaming** — Clients subscribe to instruments and receive real-time updates  
- 🔁 **Snapshots + Incrementals** — Clients receive a full snapshot on connect, followed by live updates  
- 📦 **Modular server design** — Built with `OrderBook` and `OrderBookManager` classes  
- ☁️ **AWS SQS integration** — Simulates event-driven update delivery  

---

## 📂 Project Structure

```
market_data_simulator/
├── client/                   # Client code for receiving updates
├── server/                   # Server-side logic and order book state
│   ├── config_loader.py
│   ├── main.py
│   ├── order_book.py
│   ├── order_book_manager.py
├── config/
│   └── instruments.json      # Instrument and order book depth config
├── proto/
│   └── market_data.proto     # gRPC service and message definitions
├── requirements.txt
└── README.md
```

---

## 🛠 Setup Instructions

### 1. Clone the repo and install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate gRPC Python code

```bash
python -m grpc_tools.protoc \
  -I./proto \
  --python_out=./server \
  --grpc_python_out=./server \
  ./proto/market_data.proto
```

### 3. Run the server

```bash
python server/main.py
```

### 4. Start a client *(coming soon)*

---

## 🧪 Example Config (`config/instruments.json`)

```json
{
  "instruments": [
    {
      "instrument_id": "ES",
      "order_book_depth": 5
    },
    {
      "instrument_id": "AAPL",
      "order_book_depth": 10
    }
  ]
}
```