export default function HealthScore({ data }) {
  if (!data || data.length === 0) return null;

  // Get the latest data point
  const latest = data[data.length - 1];

  // Calculate health score based on formula:
  // score = (roe*0.2 + profit_growth*0.2 + sales_growth*0.2 + (100 - debt_to_equity*10)*0.2 + cashflow_score*0.2)
  const score = (
    latest.roe * 0.2 +
    latest.profit_growth * 0.2 +
    latest.sales_growth * 0.2 +
    (100 - latest.debt_to_equity * 10) * 0.2 +
    latest.cashflow_score * 0.2
  );

  // Determine status based on score
  const getStatus = (score) => {
    if (score >= 80) return "EXCELLENT";
    if (score >= 60) return "GOOD";
    if (score >= 40) return "FAIR";
    return "POOR";
  };

  // Determine color based on score
  const getColor = (score) => {
    if (score >= 80) return "#16a34a"; // green
    if (score >= 60) return "#2563eb"; // blue
    if (score >= 40) return "#f59e0b"; // amber
    return "#dc2626"; // red
  };

  const status = getStatus(Math.round(score));
  const color = getColor(score);

  return (
    <div className="health-score-container">
      <div
        className="health-score"
        style={{
          fontSize: "36px",
          fontWeight: "bold",
          color: color,
          padding: "20px",
          backgroundColor: "rgba(0, 0, 0, 0.02)",
          borderRadius: "8px",
          marginBottom: "20px",
          textAlign: "center",
          border: `3px solid ${color}`,
        }}
      >
        <div>Health Score: {Math.round(score)}/100</div>
        <div style={{ fontSize: "24px", marginTop: "10px" }}>{status}</div>
      </div>

      <div className="score-breakdown">
        <h4>Score Breakdown:</h4>
        <ul className="breakdown-list">
          <li>ROE (20%): {latest.roe}% × 0.2 = {(latest.roe * 0.2).toFixed(2)}</li>
          <li>
            Profit Growth (20%): {latest.profit_growth}% × 0.2 ={" "}
            {(latest.profit_growth * 0.2).toFixed(2)}
          </li>
          <li>
            Sales Growth (20%): {latest.sales_growth}% × 0.2 ={" "}
            {(latest.sales_growth * 0.2).toFixed(2)}
          </li>
          <li>
            Financial Stability (20%): (100 - {latest.debt_to_equity} × 10) × 0.2 ={" "}
            {((100 - latest.debt_to_equity * 10) * 0.2).toFixed(2)}
          </li>
          <li>
            Cashflow Score (20%): {latest.cashflow_score} × 0.2 ={" "}
            {(latest.cashflow_score * 0.2).toFixed(2)}
          </li>
        </ul>
      </div>
    </div>
  );
}
