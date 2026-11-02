const BACKEND_PROD_URL = "https://finn-investment-agent.onrender.com";

export function apiUrl(path: string): string {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    // When served directly on the Render production service or running locally via Vite proxy
    if (host.includes("onrender.com") || host === "localhost" || host === "127.0.0.1") {
      return cleanPath;
    }
  }
  // When running on Netlify, Vercel, or any standalone CDN host, query the Render API backend
  return `${BACKEND_PROD_URL}${cleanPath}`;
}
