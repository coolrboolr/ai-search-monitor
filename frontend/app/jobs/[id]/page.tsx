import Link from "next/link";

type JobDetail = {
    id: number;
    title: string;
    company_name: string | null;
    location: string | null;
    posted_at: string | null;
    url: string | null;
    relevance_score: number | null;
    description: string | null;
    dedupe_key: string;
    company_classification: string | null;
    company_category: string | null;
};

const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000")
    .replace("localhost", "127.0.0.1")
    .replace(/\/$/, "");

async function getJob(id: string): Promise<JobDetail | null> {
    try {
        const res = await fetch(`${API_URL}/api/jobs/${id}`, { cache: "no-store" });
        if (!res.ok) return null;
        return res.json();
    } catch (error) {
        console.error("Failed to fetch job:", error);
        return null;
    }
}

export default async function JobDetailPage({
    params,
}: {
    params: Promise<{ id: string }>;
}) {
    const { id } = await params;
    const job = await getJob(id);

    if (!job) {
        return (
            <main className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-gray-500">Job not found.</div>
            </main>
        );
    }

    const postedLabel = job.posted_at
        ? new Date(job.posted_at).toLocaleString()
        : "Unknown";

    // Helper to separate raw signals from clean description
    const parseDescription = (desc: string | null) => {
        if (!desc) return { clean: null, signals: [] };

        // Split by " || " which seems to be the separator used by the backend
        const parts = desc.split(" || ");
        const signals: string[] = [];
        const cleanParts: string[] = [];

        parts.forEach(part => {
            const trimmed = part.trim();
            if (trimmed.startsWith("META:") || trimmed.startsWith("OPP_META:")) {
                signals.push(trimmed);
            } else {
                cleanParts.push(trimmed);
            }
        });

        return {
            clean: cleanParts.join("\n\n").trim(),
            signals
        };
    };

    const { clean: cleanDescription, signals } = parseDescription(job.description);

    return (
        <main className="min-h-screen bg-gray-50">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
                <Link
                    href="/"
                    className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
                >
                    ← Back to roles
                </Link>
                <header className="space-y-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">{job.title}</h1>
                        <p className="text-lg text-gray-700 mt-1">
                            {job.company_name} · {job.location || "Location not listed"}
                        </p>
                    </div>

                    <div className="flex flex-wrap gap-2 text-sm">
                        {job.company_classification && (
                            <span className={`inline-flex items-center px-3 py-1 rounded-full border ${job.company_classification === "Client"
                                ? "bg-blue-50 text-blue-700 border-blue-100"
                                : job.company_classification === "Competitor"
                                    ? "bg-amber-50 text-amber-700 border-amber-100"
                                    : "bg-gray-50 text-gray-700 border-gray-200"
                                }`}>
                                {job.company_classification === "Client"
                                    ? "Potential Client"
                                    : job.company_classification === "Competitor"
                                        ? "Competitor"
                                        : job.company_classification}
                            </span>
                        )}

                        {job.company_category && (
                            <span className="inline-flex items-center px-3 py-1 rounded-full bg-gray-100 text-gray-700 border border-gray-200">
                                {job.company_category}
                            </span>
                        )}

                        {job.relevance_score !== null && (
                            <span className="inline-flex items-center px-3 py-1 rounded-full bg-green-50 text-green-700 border border-green-100">
                                AI Score: {job.relevance_score?.toFixed(2)}
                            </span>
                        )}
                    </div>

                    <div className="text-sm text-gray-500">
                        Posted: {postedLabel}
                    </div>

                    {job.url && (
                        <a
                            href={job.url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-block mt-2 px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            Apply to Role ↗
                        </a>
                    )}
                </header>

                <section className="grid gap-6 md:grid-cols-2">
                    <div className="rounded-xl bg-white border border-gray-200 shadow-sm p-6">
                        <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
                            <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Athena Categorization
                        </h2>
                        <div className="space-y-4">
                            <div>
                                <p className="text-sm font-medium text-gray-500">Athena View</p>
                                <p className="text-base text-gray-900 font-medium">
                                    {job.company_classification || "Unknown"}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-500">Industry Category</p>
                                <p className="text-base text-gray-900">
                                    {job.company_category || "Unknown"}
                                </p>
                            </div>
                            <div className="pt-2 border-t border-gray-100">
                                <p className="text-xs text-gray-500 leading-relaxed">
                                    Classified using semantic analysis and OpenAI enrichment (if enabled).
                                    Check the raw metadata below for confidence scores.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="rounded-xl bg-white border border-gray-200 shadow-sm p-6">
                        <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
                            <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                            </svg>
                            System Data
                        </h2>
                        <div className="space-y-4">
                            <div>
                                <p className="text-sm font-medium text-gray-500 mb-1">Deduplication Key</p>
                                <code className="block w-full bg-gray-50 border border-gray-200 rounded p-2 text-xs font-mono text-gray-600 break-all">
                                    {job.dedupe_key}
                                </code>
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-500 mb-1">Job ID</p>
                                <span className="text-sm text-gray-900">{job.id}</span>
                            </div>
                        </div>
                    </div>
                </section>

                <section className="rounded-xl bg-white border border-gray-200 shadow-sm overflow-hidden">
                    <div className="border-b border-gray-200 bg-gray-50 px-6 py-4">
                        <h2 className="text-base font-semibold text-gray-900">
                            Description & Signals
                        </h2>
                    </div>
                    <div className="p-6">
                        {cleanDescription ? (
                            <div className="prose prose-sm max-w-none text-gray-800 whitespace-pre-wrap font-sans leading-relaxed">
                                {cleanDescription}
                            </div>
                        ) : (
                            <p className="text-sm text-gray-500 italic">No description text available.</p>
                        )}

                        {signals.length > 0 && (
                            <div className="mt-8 pt-4 border-t border-gray-100">
                                <details className="group">
                                    <summary className="flex items-center gap-2 cursor-pointer text-sm font-medium text-gray-500 hover:text-gray-700 list-none">
                                        <svg className="w-4 h-4 transition-transform group-open:rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                        </svg>
                                        View Raw Signals ({signals.length})
                                    </summary>
                                    <div className="mt-4 space-y-2 pl-6">
                                        {signals.map((signal, idx) => (
                                            <div key={idx} className="text-xs font-mono bg-gray-50 border border-gray-200 rounded p-2 text-gray-600 break-all">
                                                {signal}
                                            </div>
                                        ))}
                                    </div>
                                </details>
                            </div>
                        )}
                    </div>
                </section>
            </div>
        </main>
    );
}
