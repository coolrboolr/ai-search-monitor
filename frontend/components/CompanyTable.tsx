"use client";

import React from "react";
import { useState, useMemo, useEffect } from "react";

import Link from "next/link";

import { API_BASE } from "../lib/api";

interface Company {
    id: number;
    name: string;
    website: string | null;
    careers_url: string | null;
    category: string | null;
    region: string | null;
    classification: string | null;
    industry: string | null;
    last_seen: string | null;
    ai_search_roles: number;
    sample_titles: string | null;
}

interface Job {
    id: number;
    title: string;
    company_name: string;
    location: string | null;
    posted_at: string | null;
    url: string | null;
    relevance_score: number | null;
    source: string | null;
}

export default function CompanyTable({ companies }: { companies: Company[] }) {
    const [search, setSearch] = useState("");
    const [category, setCategory] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<"Client" | "Competitor">("Client");
    const [expandedCompanyId, setExpandedCompanyId] = useState<number | null>(null);

    const toggleCompany = (id: number) => {
        if (expandedCompanyId === id) {
            setExpandedCompanyId(null);
        } else {
            setExpandedCompanyId(id);
        }
    };

    const filtered = useMemo(
        () =>
            companies.filter((c) => {
                const matchesText =
                    !search ||
                    c.name.toLowerCase().includes(search.toLowerCase()) ||
                    (c.sample_titles ?? "").toLowerCase().includes(search.toLowerCase());
                const matchesCategory = !category || c.category === category;

                // Tab Logic
                let matchesTab = true;
                if (activeTab === "Client") {
                    // Clients are those NOT marked as Competitor (default)
                    matchesTab = c.classification !== "Competitor";
                } else {
                    matchesTab = c.classification === "Competitor";
                }

                return matchesText && matchesCategory && matchesTab;
            }),
        [companies, search, category, activeTab]
    );

    return (
        <div className="space-y-6">
            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                    <button
                        onClick={() => setActiveTab("Client")}
                        className={`
                            whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors
                            ${activeTab === "Client"
                                ? "border-blue-500 text-blue-600"
                                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"}
                        `}
                    >
                        Potential Clients
                    </button>
                    <button
                        onClick={() => setActiveTab("Competitor")}
                        className={`
                            whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors
                            ${activeTab === "Competitor"
                                ? "border-blue-500 text-blue-600"
                                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"}
                        `}
                    >
                        Competitors
                    </button>
                </nav>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
                <input
                    className="border border-gray-300 px-4 py-2 rounded-lg flex-1 focus:ring-2 focus:ring-blue-500 outline-none transition"
                    placeholder="Search by company or title..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
                <select
                    className="border border-gray-300 px-4 py-2 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 outline-none transition"
                    value={category ?? ""}
                    onChange={(e) => setCategory(e.target.value || null)}
                >
                    <option value="">All Categories</option>
                    <option value="SaaS / Tools">SaaS / Tools</option>
                    <option value="Agency / Consultancy">Agency / Consultancy</option>
                </select>
            </div>

            <div className="bg-white shadow-sm rounded-lg overflow-hidden border border-gray-200">
                <table className="w-full text-sm text-left">
                    <thead className="bg-gray-50 text-gray-700 font-medium">
                        <tr>
                            <th className="px-6 py-3 w-10"></th>
                            <th className="px-6 py-3">Company</th>
                            <th className="px-6 py-3">Roles</th>
                            <th className="px-6 py-3">Sample Titles</th>
                            <th className="px-6 py-3">Industry</th>
                            {activeTab === "Competitor" && <th className="px-6 py-3">Intel</th>}
                            <th className="px-6 py-3">Last Seen</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {filtered.map((c) => (
                            <React.Fragment key={c.id}>
                                <tr
                                    className={`
                                        hover:bg-gray-50 transition-colors cursor-pointer
                                        ${expandedCompanyId === c.id ? "bg-gray-50" : ""}
                                    `}
                                    onClick={() => toggleCompany(c.id)}
                                >
                                    <td className="px-6 py-4 text-gray-400">
                                        {expandedCompanyId === c.id ? (
                                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m18 15-6-6-6 6" /></svg>
                                        ) : (
                                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6" /></svg>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 font-semibold text-gray-900">
                                        <div onClick={(e) => e.stopPropagation()}>
                                            <a
                                                href={c.website ?? "#"}
                                                target="_blank"
                                                rel="noreferrer"
                                                className="hover:text-blue-600 hover:underline"
                                            >
                                                {c.name}
                                            </a>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                            {c.ai_search_roles}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-gray-500 max-w-xs truncate">
                                        {c.sample_titles || "-"}
                                    </td>
                                    <td className="px-6 py-4 text-gray-500">
                                        {c.industry || <span className="text-gray-400 italic">Unlabeled</span>}
                                    </td>
                                    {activeTab === "Competitor" && (
                                        <td className="px-6 py-4 text-gray-500">
                                            <button
                                                className="text-xs text-blue-600 hover:underline"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    alert("In v0 we log competitor detections for internal analysis. Deeper intel view is planned.");
                                                }}
                                            >
                                                View Intel
                                            </button>
                                        </td>
                                    )}
                                    <td className="px-6 py-4 text-gray-500">
                                        {c.last_seen ? new Date(c.last_seen).toLocaleDateString() : "-"}
                                    </td>
                                </tr>
                                {expandedCompanyId === c.id && (
                                    <tr>
                                        <td colSpan={activeTab === "Competitor" ? 7 : 6} className="px-0 py-0 border-b border-gray-100 bg-gray-50">
                                            <div className="p-4 pl-16 pr-6">
                                                <JobsList companyId={c.id} />
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </React.Fragment>
                        ))}
                        {filtered.length === 0 && (
                            <tr>
                                <td colSpan={activeTab === "Competitor" ? 7 : 6} className="px-6 py-8 text-center text-gray-500">
                                    No {activeTab === "Client" ? "potential clients" : "competitors"} found matching your filters.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function JobsList({ companyId }: { companyId: number }) {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let active = true;

        fetch(`${API_BASE}/api/companies/${companyId}/jobs`)
            .then(res => {
                if (!res.ok) throw new Error("Failed to fetch jobs");
                return res.json();
            })
            .then((data: Job[]) => {
                if (active) {
                    setJobs(data);
                    setLoading(false);
                }
            })
            .catch(err => {
                if (active) {
                    setError(err.message);
                    setLoading(false);
                }
            });

        return () => { active = false; };
    }, [companyId]);

    if (loading) return <div className="text-gray-500 text-sm py-2">Loading positions...</div>;
    if (error) return <div className="text-red-500 text-sm py-2">Error loading positions: {error}</div>;
    if (jobs.length === 0) return <div className="text-gray-500 text-sm py-2">No active positions found.</div>;

    return (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
                <thead className="bg-gray-100 text-gray-700 font-medium">
                    <tr>
                        <th className="px-4 py-2 text-left">Position</th>
                        <th className="px-4 py-2 text-left">Location</th>
                        <th className="px-4 py-2 text-left">Posted</th>
                        <th className="px-4 py-2 text-left">Source</th>
                        <th className="px-4 py-2 text-right">Action</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                    {jobs.map((job) => (
                        <tr key={job.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 font-medium text-gray-900">
                                <Link href={`/jobs/${job.id}`} className="hover:text-blue-600 hover:underline">
                                    {job.title}
                                </Link>
                            </td>
                            <td className="px-4 py-3 text-gray-500">{job.location || "Remote"}</td>
                            <td className="px-4 py-3 text-gray-500">
                                {job.posted_at ? new Date(job.posted_at).toLocaleDateString() : "Recently"}
                            </td>
                            <td className="px-4 py-3 text-gray-500 capitalize">{job.source || "-"}</td>
                            <td className="px-4 py-3 text-right">
                                <a
                                    href={job.url ?? "#"}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="text-blue-600 hover:text-blue-800 font-medium text-xs border border-blue-200 hover:border-blue-300 px-3 py-1 rounded-full bg-blue-50 hover:bg-blue-100 transition-colors"
                                >
                                    Apply
                                </a>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div >
    );
}
