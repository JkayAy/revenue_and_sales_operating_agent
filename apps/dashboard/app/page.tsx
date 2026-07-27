import { LeadQueue } from "@/components/LeadQueue";

export default function HomePage() {
  return (
    <>
      <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>Approval queue</h1>
      <p style={{ color: "#64748B", marginTop: 0, marginBottom: 24 }}>
        Review agent drafts before CRM sync (shadow mode by default).
      </p>
      <LeadQueue />
    </>
  );
}
