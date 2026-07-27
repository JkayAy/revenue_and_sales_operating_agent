# Launch Plan

---

## 1. Phases

| Phase | Audience | CRM writes | Send |
|-------|----------|------------|------|
| **Alpha** | Builder only | Off | Off |
| **Beta** | 3 design partners | Shadow / dry-run | Off |
| **Pilot** | 5–10 reps | On after approval | Copy-only / HubSpot note |
| **Public demo** | GitHub + Loom | Sandbox portal | Off |

---

## 2. Launch day checklist

- [ ] README with architecture diagram and demo GIF  
- [ ] `docker compose up` documented in [LAUNCH.md](./LAUNCH.md)  
- [ ] HubSpot sandbox webhook pointed at demo URL  
- [ ] 8-minute Loom: shadow → approve → metrics  
- [ ] Golden eval badge in CI README shield  

---

## 3. Rollback

- `kill_switch` flag stops dequeueing new runs  
- `crm_writes_enabled=false` keeps drafts without HubSpot mutations  

---

## 4. Support

- GitHub Issues for OSS demo  
- Design partners: shared Slack channel (manual)  
