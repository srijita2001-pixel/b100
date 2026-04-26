import { useEffect, useState } from "react";
import { getAnalysis } from "../api";
import Chart from "./Chart";
import HealthScore from "./HealthScore";
import ComparisonTable from "./ComparisonTable";

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [company, setCompany] = useState("HDFCBANK");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getAnalysis(company)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [company]);

  return (
    <div className="dashboard-container">
      <h1>{company} Financial Analysis</h1>

      <div className="controls">
        <label htmlFor="company-select">Select Company: </label>
        <select
          id="company-select"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
        >
          <option>HDFCBANK</option>
          <option>TCS</option>
          <option>INFY</option>
        </select>
      </div>

      {loading && <p className="loading">Loading data...</p>}
      {error && <p className="error">Error: {error}</p>}

      {!loading && !error && data.length > 0 && (
        <>
          <HealthScore data={data} />
          <Chart data={data} />
          <ComparisonTable data={data} company={company} />

          <div className="analysis-details">
            <h3>Period Analysis</h3>
            {data.map((d, i) => (
              <div key={i} className="analysis-item">
                <strong>{d.period}</strong>
                <ul>
                  <li>Sales Growth: {d.sales_growth}%</li>
                  <li>Profit Growth: {d.profit_growth}%</li>
                  <li>ROE: {d.roe}%</li>
                  <li>Debt to Equity: {d.debt_to_equity}</li>
                  <li>Cashflow Score: {d.cashflow_score}</li>
                </ul>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
