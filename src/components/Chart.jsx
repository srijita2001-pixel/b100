import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

export default function Chart({ data }) {
  const chartData = {
    labels: data.map((d) => d.period),
    datasets: [
      {
        label: "Sales Growth %",
        data: data.map((d) => d.sales_growth),
        borderColor: "#2563eb",
        backgroundColor: "rgba(37, 99, 235, 0.1)",
        tension: 0.4,
      },
      {
        label: "Profit Growth %",
        data: data.map((d) => d.profit_growth),
        borderColor: "#16a34a",
        backgroundColor: "rgba(22, 163, 74, 0.1)",
        tension: 0.4,
      },
      {
        label: "ROE %",
        data: data.map((d) => d.roe),
        borderColor: "#ea580c",
        backgroundColor: "rgba(234, 88, 12, 0.1)",
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        position: "top",
      },
      tooltip: {
        mode: "index",
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Percentage (%)",
        },
      },
      x: {
        title: {
          display: true,
          text: "Period",
        },
      },
    },
  };

  return (
    <div className="chart-container">
      <h3>Growth Metrics Over Time</h3>
      <Line data={chartData} options={options} />
    </div>
  );
}
