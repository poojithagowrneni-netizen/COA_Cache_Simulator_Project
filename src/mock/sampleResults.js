export const sampleResults = [
  { workload: "Matrix_Mult", cacheSize: "8KB",  blockSize: "32B", associativity: "1-way", replacement: "LRU",    accesses: 100000, hits: 72000, misses: 28000, hitRate: 72, missRate: 28, amat: 15 },
  { workload: "Matrix_Mult", cacheSize: "16KB", blockSize: "32B", associativity: "2-way", replacement: "LRU",    accesses: 100000, hits: 85000, misses: 15000, hitRate: 85, missRate: 15, amat: 8.5 },
  { workload: "Matrix_Mult", cacheSize: "32KB", blockSize: "64B", associativity: "2-way", replacement: "Random", accesses: 100000, hits: 88000, misses: 12000, hitRate: 88, missRate: 12, amat: 7 },
  { workload: "Matrix_Mult", cacheSize: "32KB", blockSize: "64B", associativity: "4-way", replacement: "LRU",    accesses: 100000, hits: 92000, misses: 8000,  hitRate: 92, missRate: 8,  amat: 5 },
  { workload: "Matrix_Mult", cacheSize: "64KB", blockSize: "64B", associativity: "4-way", replacement: "FIFO",   accesses: 100000, hits: 89000, misses: 11000, hitRate: 89, missRate: 11, amat: 6.5 },
  { workload: "Matrix_Mult", cacheSize: "64KB", blockSize: "64B", associativity: "8-way", replacement: "LRU",    accesses: 100000, hits: 94000, misses: 6000,  hitRate: 94, missRate: 6,  amat: 4 },
];