# API Contract (Frontend <-> Backend)

Base URL: /api  (Flask runs on http://localhost:5000)

## POST /api/simulate
Content-Type: multipart/form-data

Fields sent by the frontend:
- trace        : the uploaded trace file
- configs      : JSON string, a list of configurations
- hitTime      : number (ns)
- missPenalty  : number (ns)

Example of `configs`:

    [
      { "cacheSize": "16KB", "blockSize": "64B", "associativity": "2-way", "replacement": "LRU" },
      { "cacheSize": "32KB", "blockSize": "64B", "associativity": "4-way", "replacement": "FIFO" }
    ]

Response 200 (JSON), one result object per configuration, plus MongoDB persistence info:

    {
      "results": [
        {
          "workload": "Matrix_Mult.trace",
          "cacheSize": "16KB",
          "blockSize": "64B",
          "associativity": "2-way",
          "replacement": "LRU",
          "accesses": 100000,
          "hits": 85000,
          "misses": 15000,
          "hitRate": 85.0,
          "missRate": 15.0,
          "amat": 8.5
        }
      ],
      "savedToDb": true,
      "runId": "65e0f1..."
    }

## GET /api/health
Returns service health and MongoDB connection details:

    {
      "status": "ok",
      "service": "COA Cache Simulator API",
      "database": {
        "connected": true,
        "uri": "mongodb://localhost:27017/",
        "database": "cache_simulator",
        "version": "8.2.6",
        "error": null
      }
    }

## GET /api/db/status
Returns current MongoDB connection status.

## GET /api/history
Returns past simulation runs stored in MongoDB (ordered newest first):

    {
      "runs": [
        {
          "id": "65e0f1...",
          "workload": "Matrix_Mult.trace",
          "count": 2,
          "best": "32KB / 64B / 4-way / FIFO",
          "date": "2026-11-02 10:20:00 UTC",
          "createdAt": "2026-11-02T10:20:00+00:00",
          "hitTime": 1.0,
          "missPenalty": 50.0,
          "results": [...]
        }
      ]
    }

## GET /api/history/<id>
Returns a specific simulation run with all results.

## DELETE /api/history/<id>
Deletes a specific simulation run from MongoDB.

## DELETE /api/history
Clears all simulation runs from MongoDB.

## Rules
- Field names must match exactly (camelCase).
- hitRate and missRate are percentages (0 to 100).
- hits + misses must equal accesses.
- amat = hitTime + (misses / accesses) * missPenalty
- On error, return a non-200 status code.

## Allowed values
- cacheSize     : 8KB, 16KB, 32KB, 64KB
- blockSize     : 16B, 32B, 64B, 128B
- associativity : 1-way, 2-way, 4-way, 8-way
- replacement   : LRU, FIFO, Random

## CORS
In development the frontend uses the Vite proxy (/api -> localhost:5000).
If it is not used, enable CORS in Flask (flask-cors).

## Python implementation
The matching Flask backend is included in `backend/`.
- `backend/database.py`: MongoDB connection and collection persistence methods.
- `backend/cache/mapping.py`: direct and set-associative set-index calculation.
- `backend/cache/fifo.py`: FIFO victim selection.
- `backend/cache/lru.py`: LRU victim selection and recency updates.
- `backend/cache/random_replacement.py`: random victim selection.
- `backend/cache/simulator.py`: trace parsing, cache simulation, hit/miss rates and AMAT.
- `backend/app.py`: implements API endpoints.

See `backend/README.md` for installation, supported trace formats and test commands.
