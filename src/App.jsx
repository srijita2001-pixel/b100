import { useEffect, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function App() {
  const [data, setData] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState("HDFCBANK");
  const [selectedMetric, setSelectedMetric] = useState("sales");

  useEffect(() => {
    fetch("https://b100.onrender.com/data")
      .then((res) => res.json())
      .then((d) => setData(d))
      .catch(() => {
        // fallback JSON
        fetch("/data/fact_financials.json")
          .then((res) => res.json())
          .then((d) => setData(d));
      });
  }, []);

  const companies = [...new Set(data.map((d) => d.company))];
  const metrics = ["sales", "profit", "stock", "roe"];

  // FILTER
  const filtered = data.filter(
    (d) =>
      d.company === selectedCompany &&
      d.metric === selectedMetric
  );

  // SORT PERIOD ORDER
  const order = ["10Y", "5Y", "3Y", "TTM"];
  filtered.sort((a, b) => order.indexOf(a.period) - order.indexOf(b.period));

  // CHART DATA
  const chartData = {
    labels: filtered.map((d) => d.period),
    datasets: [
      {
        label: selectedMetric.toUpperCase() + " Growth",
        data: filtered.map((d) => d.value),
        backgroundColor: "rgba(75,192,192,0.6)",
      },
    ],
  };

  // =====================
  // NORMALIZATION
  // =====================
  const normalize = (value, min, max) => {
    if (max === min) return 50;
    return ((value - min) / (max - min)) * 100;
  };

  const getScore = (company) => {
    const companyData = data.filter((d) => d.company === company);

    const metrics = ["sales", "profit", "roe", "stock"];

    let score = 0;

    metrics.forEach((metric) => {
      const values = data
        .filter((d) => d.metric === metric)
        .map((d) => d.value);

      const min = Math.min(...values);
      const max = Math.max(...values);

      const val =
        companyData.find((d) => d.metric === metric && d.period === "TTM")
          ?.value || 0;

      score += normalize(val, min, max);
    });

    return score / 4;
  };

  const getInsight = (score) => {
    if (score > 70) return "🟢 Strong";
    if (score > 40) return "🟡 Average";
    return "🔴 Weak";
  };

  const getReason = (company) => {
    const companyData = data.filter((d) => d.company === company);

    const best = companyData.reduce((a, b) =>
      a.value > b.value ? a : b
    );

    const worst = companyData.reduce((a, b) =>
      a.value < b.value ? a : b
    );

    return `Strongest in ${best.metric.toUpperCase()} (${best.value}%), weakest in ${worst.metric.toUpperCase()} (${worst.value}%)`;
  };

  // TOP COMPANIES
  const ranking = companies
    .map((c) => ({
      company: c,
      score: getScore(c),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);

  return (
    <div style={{ padding: "20px" }}>
      <h1>📊 B100 Financial Intelligence</h1>

      {/* FILTERS */}
      <select onChange={(e) => setSelectedCompany(e.target.value)}>
        {companies.map((c) => (
          <option key={c}>{c}</option>
        ))}
      </select>

      <select onChange={(e) => setSelectedMetric(e.target.value)}>
        {metrics.map((m) => (
          <option key={m}>{m}</option>
        ))}
      </select>

      <h2>
        {selectedCompany} - {selectedMetric.toUpperCase()} Trend
      </h2>

      <Bar data={chartData} />

      {/* TOP COMPANIES */}
      <h2>🏆 Top 5 Companies</h2>

      {ranking.map((r, i) => (
        <div key={i} style={{ marginBottom: "10px" }}>
          <b>
            {i + 1}. {r.company}
          </b>{" "}
          → Score: {r.score.toFixed(1)} {getInsight(r.score)}
          <br />
          <small>{getReason(r.company)}</small>
          <hr />
        </div>
      ))}
    </div>
  );
}