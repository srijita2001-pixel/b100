export default function ComparisonTable({ data, company }) {
  if (!data || data.length === 0) return null;

  // Sample comparison data for all companies
  const comparisonData = [
    { name: "HDFCBANK", roe: 16.5, cagr: 12.5, score: 72 },
    { name: "TCS", roe: 18.2, cagr: 14.0, score: 78 },
    { name: "INFY", roe: 17.8, cagr: 13.5, score: 75 },
  ];

  return (
    <div className="comparison-table-container">
      <h3>Company Comparison</h3>
      <table className="comparison-table">
        <thead>
          <tr>
            <th>Company</th>
            <th>ROE (%)</th>
            <th>CAGR (%)</th>
            <th>Health Score</th>
          </tr>
        </thead>
        <tbody>
          {comparisonData.map((comp, idx) => (
            <tr key={idx} className={comp.name === company ? "active-row" : ""}>
              <td className="company-name">{comp.name}</td>
              <td>{comp.roe}</td>
              <td>{comp.cagr}</td>
              <td>
                <span
                  className="score-badge"
                  style={{
                    backgroundColor:
                      comp.score >= 75
                        ? "rgba(22, 163, 74, 0.2)"
                        : "rgba(37, 99, 235, 0.2)",
                    color: comp.score >= 75 ? "#16a34a" : "#2563eb",
                    padding: "4px 8px",
                    borderRadius: "4px",
                    fontWeight: "600",
                  }}
                >
                  {comp.score}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
