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

Response 200 (JSON), one result object per configuration:

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
      ]
    }

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