export interface Stats {
    total_companies: number;
    total_jobs: number;
    total_competitors: number;
    total_clients: number;
    last_ingestion_at: string | null;
}

export default function StatsBar({ stats }: { stats: Stats | null }) {
    if (!stats) {
        return null;
    }

    const {
        total_companies,
        total_jobs,
        total_competitors,
        total_clients,
        last_ingestion_at,
    } = stats;

    const lastRunLabel = last_ingestion_at
        ? new Date(last_ingestion_at).toLocaleString()
        : "No data yet";

    return (
        <section className="mb-8">
            <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                <div className="rounded-xl border border-gray-200 bg-white px-4 py-3 shadow-sm">
                    <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Companies
                    </div>
                    <div className="mt-1 text-2xl font-semibold text-gray-900">
                        {total_companies}
                    </div>
                </div>

                <div className="rounded-xl border border-gray-200 bg-white px-4 py-3 shadow-sm">
                    <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        AI Search Roles
                    </div>
                    <div className="mt-1 text-2xl font-semibold text-gray-900">
                        {total_jobs}
                    </div>
                </div>

                <div className="rounded-xl border border-gray-200 bg-white px-4 py-3 shadow-sm">
                    <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Potential Clients
                    </div>
                    <div className="mt-1 text-2xl font-semibold text-gray-900">
                        {total_clients}
                    </div>
                </div>

                <div className="rounded-xl border border-gray-200 bg-white px-4 py-3 shadow-sm">
                    <div className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Competitors
                    </div>
                    <div className="mt-1 text-2xl font-semibold text-gray-900">
                        {total_competitors}
                    </div>
                    <p className="mt-1 text-[11px] text-gray-500">
                        Last run: {lastRunLabel}
                    </p>
                </div>
            </div>
        </section>
    );
}
