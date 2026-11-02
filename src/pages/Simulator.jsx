import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { runSimulation } from "../api/client.js";

const OPTIONS = {
  cacheSize: ["8KB", "16KB", "32KB", "64KB"],
  blockSize: ["16B", "32B", "64B", "128B"],
  associativity: ["1-way", "2-way", "4-way", "8-way"],
  replacement: ["LRU", "FIFO", "Random"],
};

function CheckboxGroup({ title, options, selected, onToggle }) {
  return (
    <div className="group">
      <p className="group-title">{title}</p>
      <div className="check-row">
        {options.map((opt) => (
          <label key={opt} className="check">
            <input
              type="checkbox"
              checked={selected.includes(opt)}
              onChange={() => onToggle(opt)}
            />
            {opt}
          </label>
        ))}
      </div>
    </div>
  );
}

export default function Simulator() {
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [selected, setSelected] = useState({
    cacheSize: ["8KB", "16KB", "32KB", "64KB"],
    blockSize: ["64B"],
    associativity: ["1-way", "2-way", "4-way"],
    replacement: ["LRU"],
  });
  const [hitTime, setHitTime] = useState(1);
  const [missPenalty, setMissPenalty] = useState(50);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const toggle = (group, value) => {
    setSelected((prev) => {
      const current = prev[group];
      const updated = current.includes(value)
        ? current.filter((v) => v !== value)
        : [...current, value];
      return { ...prev, [group]: updated };
    });
  };

  const combos = selected.cacheSize.flatMap((cs) =>
    selected.blockSize.flatMap((bs) =>
      selected.associativity.flatMap((a) =>
        selected.replacement.map((p) => ({
          cacheSize: cs,
          blockSize: bs,
          associativity: a,
          replacement: p,
        }))
      )
    )
  );

  const handleRun = async () => {
    if (!file) return setError("Please upload a trace file.");
    if (combos.length === 0)
      return setError("Select at least one option in every group.");
    if (!(hitTime > 0) || !(missPenalty > 0))
      return setError("Hit time and miss penalty must be positive numbers.");

    setError("");
    setLoading(true);

    try {
      const results = await runSimulation({
        file,
        configs: combos,
        hitTime,
        missPenalty,
      });

      localStorage.setItem("lastResults", JSON.stringify(results));

      const best = [...results].sort(
        (a, b) => a.amat - b.amat || b.hitRate - a.hitRate
      )[0];
      const history = JSON.parse(localStorage.getItem("runHistory") || "[]");
      history.unshift({
        id: Date.now(),
        date: new Date().toLocaleString(),
        workload: file.name,
        count: results.length,
        best: `${best.cacheSize} / ${best.blockSize} / ${best.associativity} / ${best.replacement}`,
        results,
      });
      localStorage.setItem("runHistory", JSON.stringify(history));

      navigate("/results");
    } catch (err) {
      setError("Simulation failed. Please check that the backend is running and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Run Simulation</h2>

      <div className="form-card">
        <h3>Step 1: Upload Trace File</h3>
        <input
          type="file"
          accept=".trace,.txt,.csv,.out,.log"
          onChange={(e) => setFile(e.target.files[0] || null)}
        />
        {file ? (
          <p className="file-info">
            Selected: <strong>{file.name}</strong> ({(file.size / 1024).toFixed(1)} KB)
          </p>
        ) : (
          <p className="muted">No file selected yet.</p>
        )}
      </div>

      <div className="form-card">
        <h3>Step 2: Cache Configuration</h3>
        <CheckboxGroup title="Cache Size" options={OPTIONS.cacheSize} selected={selected.cacheSize} onToggle={(v) => toggle("cacheSize", v)} />
        <CheckboxGroup title="Block Size" options={OPTIONS.blockSize} selected={selected.blockSize} onToggle={(v) => toggle("blockSize", v)} />
        <CheckboxGroup title="Associativity" options={OPTIONS.associativity} selected={selected.associativity} onToggle={(v) => toggle("associativity", v)} />
        <CheckboxGroup title="Replacement Policy" options={OPTIONS.replacement} selected={selected.replacement} onToggle={(v) => toggle("replacement", v)} />
      </div>

      <div className="form-card">
        <h3>Step 3: Timing</h3>
        <div className="fields">
          <label className="field">
            Hit Time (ns)
            <input type="number" min="0" step="any" value={hitTime} onChange={(e) => setHitTime(Number(e.target.value))} />
          </label>
          <label className="field">
            Miss Penalty (ns)
            <input type="number" min="0" step="any" value={missPenalty} onChange={(e) => setMissPenalty(Number(e.target.value))} />
          </label>
        </div>
      </div>

      <p className="muted">
        <strong>{combos.length}</strong> configuration{combos.length === 1 ? "" : "s"} will be tested.
      </p>

      {error && <p className="error">{error}</p>}

      <button className="btn" onClick={handleRun} disabled={loading}>
        {loading ? "Running simulation..." : "Run Simulation"}
      </button>
    </div>
  );
}