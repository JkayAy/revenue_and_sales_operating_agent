from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class IcpConfig:
    employee_count_min: int = 50
    employee_count_max: int = 500
    allowed_countries: list[str] = field(default_factory=lambda: ["US", "GB", "DE"])
    blocked_industries: list[str] = field(default_factory=lambda: ["gambling", "adult"])


@dataclass
class OutreachConfig:
    max_drafts_per_lead_per_day: int = 2
    required_citations_min: int = 1
    tone: str = "consultative"


@dataclass
class PipelineConfig:
    on_approve_first_touch_deal_stage_id: str = "attempting_contact"
    require_approval_for_stage_change: bool = True


@dataclass
class PlaybookConfig:
    icp: IcpConfig = field(default_factory=IcpConfig)
    outreach: OutreachConfig = field(default_factory=OutreachConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)


def load_playbook_config(path: Path | str | None = None) -> PlaybookConfig:
    if path is None:
        return PlaybookConfig()
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    icp = data.get("icp", {})
    outreach = data.get("outreach", {})
    pipeline = data.get("pipeline", {})
    on_approve = pipeline.get("on_approve_first_touch", {})
    return PlaybookConfig(
        icp=IcpConfig(
            employee_count_min=int(icp.get("employee_count_min", 50)),
            employee_count_max=int(icp.get("employee_count_max", 500)),
            allowed_countries=[c.upper() for c in icp.get("allowed_countries", ["US", "GB", "DE"])],
            blocked_industries=[i.lower() for i in icp.get("blocked_industries", ["gambling", "adult"])],
        ),
        outreach=OutreachConfig(
            max_drafts_per_lead_per_day=int(outreach.get("max_drafts_per_lead_per_day", 2)),
            required_citations_min=int(outreach.get("required_citations_min", 1)),
            tone=str(outreach.get("tone", "consultative")),
        ),
        pipeline=PipelineConfig(
            on_approve_first_touch_deal_stage_id=str(
                on_approve.get("deal_stage_id", "attempting_contact")
            ),
            require_approval_for_stage_change=bool(
                pipeline.get("require_approval_for_stage_change", True)
            ),
        ),
    )
