"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { apiBase, fetchJson } from "@/lib/api";

type LeadRow = {
  lead_id: string;
  email: string;
  company?: string;
  first_name?: string;
  status: string;
  qualified?: boolean;
};

export function LeadQueue() {
  const [leads, setLeads] = useState<LeadRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchJson<{ leads: LeadRow[] }>(`${apiBase()}/v1/leads`);
      setLeads(data.leads);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function ingestSample() {
    await fetchJson(`${apiBase()}/v1/leads/ingest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: `sample+${Date.now()}@acme.io`,
        first_name: "Jordan",
        company: "Acme Analytics",
        employee_count: 120,
        country: "US",
        industry: "software",
      }),
    });
    await load();
  }

  if (loading) return <p>Loading…</p>;
  if (error) {
    return (
      <div style={{ color: "#DC2626" }}>
        <p>{error}</p>
        <p style={{ fontSize: 14 }}>
          Start API: <code>sales-api</code> at {apiBase()}
        </p>
      </div>
    );
  }

  return (
    <div>
      <button
        type="button"
        onClick={ingestSample}
        style={{
          background: "#2563EB",
          color: "#fff",
          border: "none",
          borderRadius: 8,
          padding: "8px 14px",
          cursor: "pointer",
          marginBottom: 16,
        }}
      >
        Ingest sample lead
      </button>
      <table style={{ width: "100%", background: "#fff", borderRadius: 8, borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid #E2E8F0" }}>
            <th style={{ padding: 12 }}>Company</th>
            <th style={{ padding: 12 }}>Contact</th>
            <th style={{ padding: 12 }}>Status</th>
            <th style={{ padding: 12 }}></th>
          </tr>
        </thead>
        <tbody>
          {leads.length === 0 && (
            <tr>
              <td colSpan={4} style={{ padding: 24, color: "#64748B" }}>
                No leads yet — ingest a sample or POST to /v1/leads/ingest
              </td>
            </tr>
          )}
          {leads.map((l) => (
            <tr key={l.lead_id} style={{ borderBottom: "1px solid #F1F5F9" }}>
              <td style={{ padding: 12 }}>{l.company ?? "—"}</td>
              <td style={{ padding: 12 }}>
                {l.first_name ? `${l.first_name} · ` : ""}
                {l.email}
              </td>
              <td style={{ padding: 12 }}>
                <StatusBadge status={l.status} />
              </td>
              <td style={{ padding: 12 }}>
                <Link href={`/leads/${l.lead_id}`} style={{ color: "#2563EB" }}>
                  Open
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    awaiting_approval: "#2563EB",
    approved: "#059669",
    rejected: "#64748B",
    disqualified: "#64748B",
    failed: "#DC2626",
    processing: "#D97706",
  };
  return (
    <span style={{ color: colors[status] ?? "#0F172A", fontSize: 13, fontWeight: 500 }}>
      {status.replace(/_/g, " ")}
    </span>
  );
}
