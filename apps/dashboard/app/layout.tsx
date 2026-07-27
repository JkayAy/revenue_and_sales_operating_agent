export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "Inter, system-ui, sans-serif", background: "#F8FAFC" }}>
        <header
          style={{
            background: "#fff",
            borderBottom: "1px solid #E2E8F0",
            padding: "12px 24px",
            display: "flex",
            alignItems: "center",
            gap: 24,
          }}
        >
          <strong style={{ color: "#0F172A" }}>PipelinePilot</strong>
          <nav style={{ display: "flex", gap: 16, fontSize: 14 }}>
            <a href="/" style={{ color: "#2563EB", textDecoration: "none" }}>
              Queue
            </a>
            <a href="/metrics" style={{ color: "#64748B", textDecoration: "none" }}>
              Metrics
            </a>
          </nav>
        </header>
        <main style={{ maxWidth: 1200, margin: "0 auto", padding: 24 }}>{children}</main>
      </body>
    </html>
  );
}
