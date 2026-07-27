"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { apiBase, fetchJson } from "@/lib/api";

type LeadDetail = {
  lead_id: string;
  email: string;
  company?: string;
  status: string;
  run?: {
    draft?: { subject: string; body: string };
    research?: { sources?: { title: string; url: string }[] };
    enrichment?: Record<string, unknown>;
    tool_runs?: { tool_name: string; status: string }[];
  };
};

export default function LeadDetailPage({ params }: { params: { lead_id: string } }) {
  const router = useRouter();
  const [lead, setLead] = useState<LeadDetail | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const data = await fetchJson<LeadDetail>(`${apiBase()}/v1/leads/${params.lead_id}`);
    setLead(data);
  }, [params.lead_id]);

  useEffect(() => {
    load().catch(() => setLead(null));
  }, [load]);

  async function approve() {
    setBusy(true);
    try {
      await fetchJson(`${apiBase()}/v1/leads/${params.lead_id}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ editor_user_id: "demo-rep" }),
      });
      await load();
      router.refresh();
    } finally {
      setBusy(false);
    }
  }

  async function reject() {
    setBusy(true);
    try {
      await fetchJson(`${apiBase()}/v1/leads/${params.lead_id}/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ actor_user_id: "demo-rep", reason: "Not a fit" }),
      });
      await load();
    } finally {
      setBusy(false);
    }
  }

  if (!lead) return <p>Loading or not found.</p>;

  const draft = lead.run?.draft;
  const sources = lead.run?.research?.sources ?? [];

  return (
    <div>
      <a href="/" style={{ color: "#64748B", fontSize: 14 }}>
        ← Queue
      </a>
      <h1 style={{ fontSize: 24, fontWeight: 600 }}>{lead.company ?? lead.email}</h1>
      <p style={{ color: "#64748B" }}>
        Status: <strong>{lead.status}</strong>
      </p>

      {sources.length > 0 && (
        <section style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 16 }}>Sources</h2>
          <ul>
            {sources.map((s) => (
              <li key={s.url}>
                <a href={s.url} target="_blank" rel="noreferrer">
                  {s.title}
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}

      {draft && (
        <section
          style={{
            background: "#fff",
            padding: 20,
            borderRadius: 8,
            marginBottom: 24,
            whiteSpace: "pre-wrap",
          }}
        >
          <h2 style={{ fontSize: 16, marginTop: 0 }}>{draft.subject}</h2>
          <p style={{ lineHeight: 1.5 }}>{draft.body}</p>
        </section>
      )}

      {lead.status === "awaiting_approval" && (
        <div style={{ display: "flex", gap: 12 }}>
          <button
            type="button"
            disabled={busy}
            onClick={approve}
            style={{
              background: "#2563EB",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              padding: "10px 16px",
              cursor: "pointer",
            }}
          >
            Approve
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={reject}
            style={{
              background: "#fff",
              color: "#DC2626",
              border: "1px solid #FECACA",
              borderRadius: 8,
              padding: "10px 16px",
              cursor: "pointer",
            }}
          >
            Reject
          </button>
        </div>
      )}
    </div>
  );
}
