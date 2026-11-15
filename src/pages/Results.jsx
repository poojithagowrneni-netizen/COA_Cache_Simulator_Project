import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { sampleResults } from "../mock/sampleResults.js";

function loadResults() {
  try {
    const saved = localStorage.getItem("lastResults");
    const parsed = saved ? JSON.parse(saved) : null;
    return Array.isArray(parsed) && parsed.length > 0 ? parsed : sampleResults;
  } catch {
    return sampleResults;
  }
}

function downloadCSV(results) {
  const headers = ["Workload", "Cache Size", "Block Size", "Associativity", "Replacement", "Accesses", "Hits", "Misses", "Hit Rate", "Miss Rate", "AMAT (ns)"];
  const rows = results.map((r) => [
    `"${r.workload}"`, r.cacheSize, r.blockSize, r.associativity, r.replacement,
    r.accesses, r.hits, r.misses, r.hitRate, r.missRate, r.amat,
  ]);
  const csv = [headers, ...rows].map((row) => row.join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "cache_results.csv";
  a.click();
  URL.revokeObjectURL(url);
}

function MetricChart({ title, data, dataKey, color }) {
  return (
    <div className="chart-box">
      <h4>{title}</h4>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 10, right: 15, left: 15, bottom: 65 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 9 }}
            interval={0}
            angle={-35}
            textAnchor="end"
            height={85}
          />
          <YAxis domain={dataKey === "hitRate" ? [0, 100] : ["auto", "auto"]} />
          <Tooltip
            formatter={(value) => [
              dataKey === "hitRate" || dataKey === "missRate" ? `${value}%` : `${value} ns`,
              dataKey,
            ]}
          />
          <Bar dataKey={dataKey} fill={color} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function Results() {
  const results = loadResults();
  const best = [...results].sort((a, b) => a.amat - b.amat || b.hitRate - a.hitRate)[0];

  const chartData = results.map((r) => ({
    ...r,
    label: `${r.cacheSize}/${r.blockSize}/${r.associativity}/${r.replacement}`,
  }));

  return (
    <div>
      <div className="history-head">
        <h2>Results: {results[0].workload}</h2>
        <button className="btn btn-small" onClick={() => downloadCSV(results)}>
          Download CSV
        </button>
      </div>

      <div className="cards">
        <div className="card">
          <p className="card-label">Accesses</p>
          <p className="card-value">{best.accesses.toLocaleString()}</p>
        </div>
        <div className="card">
          <p className="card-label">Hits</p>
          <p className="card-value">{best.hits.toLocaleString()}</p>
        </div>
        <div className="card">
          <p className="card-label">Misses</p>
          <p className="card-value">{best.misses.toLocaleString()}</p>
        </div>
        <div className="card">
          <p className="card-label">Hit Rate</p>
          <p className="card-value">{best.hitRate}%</p>
        </div>
      </div>

      <div className="best">
        <h3>BEST CONFIGURATION:</h3>
        <p>
          {best.cacheSize} cache · {best.blockSize} block · {best.associativity} · {best.replacement}
        </p>
        <p>
          Hit Rate: <strong>{best.hitRate}%</strong> &nbsp; AMAT: <strong>{best.amat} ns</strong>
        </p>
      </div>

      <div className="chart-grid">
        <MetricChart title="Hit Rate Comparison (%)" data={chartData} dataKey="hitRate" color="#2e9e5b" />
        <MetricChart title="Miss Rate Comparison (%)" data={chartData} dataKey="missRate" color="#d64545" />
        <MetricChart title="AMAT Comparison (ns, lower is better)" data={chartData} dataKey="amat" color="#2f6fd6" />
      </div>

      <h3>All Configurations</h3>
      <table>
        <thead>
          <tr>
            <th>Cache Size</th>
            <th>Block Size</th>
            <th>Associativity</th>
            <th>Policy</th>
            <th>Hit Rate</th>
            <th>Miss Rate</th>
            <th>AMAT (ns)</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r, i) => (
            <tr key={i} className={r === best ? "best-row" : ""}>
              <td>{r.cacheSize}</td>
              <td>{r.blockSize}</td>
              <td>{r.associativity}</td>
              <td>{r.replacement}</td>
              <td>{r.hitRate}%</td>
              <td>{r.missRate}%</td>
              <td>{r.amat}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
