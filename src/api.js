const API_URL = import.meta.env.VITE_API_URL;

export const getAnalysis = async (company) => {
  const res = await fetch(`${API_URL}/api/analysis?company=${company}`);
  return res.json();
};
