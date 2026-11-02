import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

function loadRuns() {
  try {
    const saved = JSON.parse(localStorage.getItem("runHistory") || "[]");
    return Array.isArray(saved) ? saved : [];
  } catch (err) {
    return [];
  }
}

export default function History() {
  const navigate = useNavigate();
  const [runs, setRuns] = useState(loadRuns);

  const view = (run) => {
    localStorage.setItem("lastResults", JSON.stringify(run.results));
    navigate("/results");
  };

  const remove = (id) => {
    const updated = runs.filter((r) => r.id !== id);
    localStorage.setItem("runHistory", JSON.stringify(updated));
    setRuns(updated);
  };

  const clearAll = () => {
    localStorage.removeItem("runHistory");
    setRuns([]);
  };

  if (runs.length === 0) {
    return (
      <div>
        <h2>Past Simulations</h2>
        <p className="muted">No simulations yet.</p>
        <Link to="/simulator" className="btn">Start your first one</Link>
      </div>
    );
  }

  return (
    <div>
      <div className="history-head">
        <h2>Past Simulations</h2>
        <button className="btn btn-danger btn-small" onClick={clearAll}>Clear All</button>
      </div>

      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Workload</th>
            <th>Configs</th>
            <th>Best Configuration</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.id}>
              <td>{run.date}</td>
              <td>{run.workload}</td>
              <td>{run.count}</td>
              <td>{run.best}</td>
              <td className="actions">
                <button className="btn btn-small" onClick={() => view(run)}>View</button>
                <button className="btn btn-small btn-danger" onClick={() => remove(run.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}