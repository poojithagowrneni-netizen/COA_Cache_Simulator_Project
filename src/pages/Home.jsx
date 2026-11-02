import { Link } from "react-router-dom";

const steps = [
  { n: 1, title: "Upload", text: "Choose a memory access trace file." },
  { n: 2, title: "Configure", text: "Pick cache size, block size, associativity and replacement policy." },
  { n: 3, title: "Simulate", text: "Run the cache simulator on every configuration." },
  { n: 4, title: "Analyze", text: "Compare hit rate, miss rate and AMAT, and see the best configuration." },
];

export default function Home() {
  return (
    <div>
      <div className="hero">
        <h1>Cache Memory Performance Analyzer</h1>
        <p>
          Upload a memory trace, test different cache configurations, and find
          the one with the best hit rate and lowest AMAT.
        </p>
        <Link to="/simulator" className="btn btn-gold">Start Simulation</Link>
      </div>

      <h3>How it works</h3>
      <div className="steps">
        {steps.map((s) => (
          <div className="step" key={s.n}>
            <div className="step-num">{s.n}</div>
            <h4>{s.title}</h4>
            <p>{s.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}