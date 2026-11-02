import axios from "axios";

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
});

function fakeSimulate(workload, combos, hitTime, missPenalty) {
  const accesses = 100000;
  return combos.map((c) => {
    const sizeKB = parseInt(c.cacheSize);
    const block = parseInt(c.blockSize);
    const ways = parseInt(c.associativity);

    let rate =
      55 +
      Math.log2(sizeKB / 8) * 9 +
      Math.log2(ways) * 3 +
      (block === 64 ? 4 : block === 32 ? 2.5 : block === 128 ? 1 : 0) +
      (c.replacement === "LRU" ? 1.5 : c.replacement === "FIFO" ? 0.5 : 0) +
      Math.random();
    rate = Math.min(99, Math.max(30, rate));

    const hits = Math.round((accesses * rate) / 100);
    const misses = accesses - hits;

    return {
      workload,
      ...c,
      accesses,
      hits,
      misses,
      hitRate: +((hits / accesses) * 100).toFixed(2),
      missRate: +((misses / accesses) * 100).toFixed(2),
      amat: +(hitTime + (misses / accesses) * missPenalty).toFixed(2),
    };
  });
}

export async function runSimulation({ file, configs, hitTime, missPenalty }) {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 1200));
    return fakeSimulate(file.name, configs, hitTime, missPenalty);
  }

  const form = new FormData();
  form.append("trace", file);
  form.append("configs", JSON.stringify(configs));
  form.append("hitTime", hitTime);
  form.append("missPenalty", missPenalty);

  const response = await http.post("/simulate", form);
  return response.data.results;
}