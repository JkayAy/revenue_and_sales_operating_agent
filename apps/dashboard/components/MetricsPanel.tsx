"use client";

import { useEffect, useState } from "react";

import { apiBase, fetchJson } from "@/lib/api";

export function MetricsPanel() {
  const [metrics, setMetrics] = useState<Record<string, number> | null>(null);

  useEffect(() => {
    fetchJson<Record<string, number>>(`${apiBase()}/v1/admin/metrics`)
      .then(setMetrics)
      .catch(() => setMetrics(null));
  }, []);

  if (!metrics) return <p>Could not load metrics — is the API running?</p>;

  const tiles = [
    { label: "Total leads", key: "total_leads" },
    { label: "Queue depth", key: "queue_depth" },
    { label: "Drafts ready", key: "draft_ready_count" },
    { label: "Approved", key: "approval_count" },
  ];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 16 }}>
      {tiles.map((t) => (
        <div
          key={t.key}
          style={{
            background: "#fff",
            borderRadius: 8,
            padding: 20,
            boxShadow: "0 1px 2px rgb(0 0 0 / 0.06)",
          }}
        >
          <div style={{ fontSize: 12, color: "#64748B" }}>{t.label}</div>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{metrics[t.key] ?? 0}</div>
        </div>
      ))}
    </div>
  );
}
