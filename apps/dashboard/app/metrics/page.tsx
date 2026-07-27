import { MetricsPanel } from "@/components/MetricsPanel";

export default function MetricsPage() {
  return (
    <>
      <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: 24 }}>RevOps metrics</h1>
      <MetricsPanel />
    </>
  );
}
