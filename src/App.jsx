import { Routes, Route, NavLink } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Simulator from "./pages/Simulator.jsx";
import Results from "./pages/Results.jsx";
import History from "./pages/History.jsx";

export default function App() {
  return (
    <div>
      <nav className="navbar">
        <span className="brand">Cache Memory Performance Analyzer</span>
        <div className="links">
          <NavLink to="/">Home</NavLink>
          <NavLink to="/simulator">Simulator</NavLink>
          <NavLink to="/results">Results</NavLink>
          <NavLink to="/history">History</NavLink>
        </div>
      </nav>

      <main className="page">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/simulator" element={<Simulator />} />
          <Route path="/results" element={<Results />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
    </div>
  );
}