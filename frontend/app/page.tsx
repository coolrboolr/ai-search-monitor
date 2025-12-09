import CompanyTable from "@/components/CompanyTable";
import StatsBar, { Stats } from "@/components/StatsBar";

// Function to fetch data. In production this would handle errors/timeouts better.
// Assuming backend runs on localhost:8000 by default, or use env var.
const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

// Function to fetch data. In production this would handle errors/timeouts better.
// Assuming backend runs on localhost:8000
async function getCompanies() {
  try {
    const res = await fetch(`${API_URL}/api/companies?min_roles=1`, {
      cache: "no-store",
    });

    if (!res.ok) {
      console.error("Failed to fetch companies", res.status);
      return [];
    }
    return res.json();
  } catch (e) {
    console.error("Error fetching companies:", e);
    return [];
  }
}

async function getStats(): Promise<Stats | null> {
  try {
    const res = await fetch(`${API_URL}/api/stats`, {
      cache: "no-store",
    });
    if (!res.ok) {
      console.error("Failed to fetch stats", res.status);
      return null;
    }
    return (await res.json()) as Stats;
  } catch (e) {
    console.error("Error fetching stats:", e);
    return null;
  }
}

export default async function HomePage() {
  const [companies, stats] = await Promise.all([getCompanies(), getStats()]);

  return (
    <main className="min-h-screen bg-gray-50 font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <header className="mb-10">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
            AI Search <span className="text-blue-600">Monitor</span>
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Tracking the hiring pulse of the AI Search revolution.
          </p>
        </header>

        <StatsBar stats={stats} />

        <CompanyTable companies={companies} />
      </div>
    </main>
  );
}
