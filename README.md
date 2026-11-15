# COA Cache Memory Performance Analyzer

A full-stack trace-driven cache memory performance simulator with an interactive React/Vite frontend, a Python/Flask simulation engine, and MongoDB persistence.

---

## 🚀 Quick Start

### macOS / Linux
Run the all-in-one launcher script from the project root:
```bash
./start_servers.sh
```

### Windows
Run the batch launcher script:
```cmd
start_servers.bat
```

Once running:
- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🛠 Project Structure

```
COA_Cache_Simulator_Project/
├── start_servers.sh            # macOS / Linux unified launcher
├── start_servers.bat           # Windows unified launcher
├── COA_Cache_Simulator_Project.zip # Standalone distributable archive
└── cache_build/
    └── COA FRONTEND/
        ├── backend/
        │   ├── app.py          # Flask REST API endpoints
        │   ├── database.py     # MongoDB persistence layer
        │   ├── requirements.txt # Python dependencies
        │   ├── cache/
        │   │   ├── mapping.py  # Cache mapping algorithms
        │   │   ├── lru.py      # Least-Recently-Used policy
        │   │   ├── fifo.py     # First-In-First-Out policy
        │   │   ├── random_replacement.py # Random eviction policy
        │   │   └── simulator.py # Trace parser & simulation engine
        │   └── tests/          # Automated backend unit tests
        ├── src/
        │   ├── App.jsx         # Code-split router & database status pill
        │   ├── api/client.js   # API client & localStorage fallback
        │   ├── pages/
        │   │   ├── Home.jsx    # Overview & getting started
        │   │   ├── Simulator.jsx # Configuration form & trace upload
        │   │   ├── Results.jsx # Performance metrics, charts & CSV export
        │   │   └── History.jsx # MongoDB simulation run history
        │   └── mock/           # Fallback mock data
        ├── tester_bot.py       # Comprehensive verification bot
        ├── vite.config.js      # Vite build config with vendor chunking
        ├── package.json        # Frontend dependencies
        └── sample.trace        # Benchmark trace file
```

---

## 📊 Features

- **Mapping Strategies**: Direct Mapped (`1-way`), N-Way Set Associative (`2-way`, `4-way`, `8-way`), and Fully Associative.
- **Eviction Policies**: LRU (Least Recently Used), FIFO (First-In-First-Out), and Random.
- **Trace Support**: Hexadecimal (`0x...`), CSV tables, Dinero IV format, and Valgrind lackey logs.
- **Metrics Computed**: Total accesses, cache hits, cache misses, hit rate (%), miss rate (%), and AMAT (Average Memory Access Time in ns).
- **MongoDB Persistence**: Simulation runs and historical benchmarks are persisted to MongoDB (`cache_simulator` database) with full fallback support.
- **Optimized Frontend**: Route-level code-splitting with `React.lazy()` and `Suspense`, isolating heavy dependencies like Recharts for fast initial page loads.

---

## 🧪 Testing

To run the complete automated test suite (backend unit tests, frontend oxlint, and production build):

```bash
cd "cache_build/COA FRONTEND"
.venv/bin/python tester_bot.py
```
