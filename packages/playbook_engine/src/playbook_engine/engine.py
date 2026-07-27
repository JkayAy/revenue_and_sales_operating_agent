from playbook_engine.config import PlaybookConfig
from playbook_engine.decisions import PlaybookDecision, PlaybookOutcome


class PlaybookEngine:
    def __init__(self, config: PlaybookConfig | None = None) -> None:
        self.config = config or PlaybookConfig()

    def evaluate_icp(
        self,
        *,
        employee_count: int | None,
        country: str | None,
        industry: str | None,
    ) -> PlaybookDecision:
        cfg = self.config.icp
        if industry and industry.strip().lower() in cfg.blocked_industries:
            return PlaybookDecision(
                PlaybookOutcome.DENY,
                "icp_blocked_industry",
                f"Industry '{industry}' is excluded from outbound.",
            )
        if country:
            cc = country.strip().upper()
            if cc not in cfg.allowed_countries:
                return PlaybookDecision(
                    PlaybookOutcome.DENY,
                    "icp_geo_denied",
                    f"Country '{country}' is outside the ICP.",
                )
        if employee_count is None:
            return PlaybookDecision(
                PlaybookOutcome.DENY,
                "icp_missing_headcount",
                "Employee count is required for ICP qualification.",
            )
        if employee_count < cfg.employee_count_min:
            return PlaybookDecision(
                PlaybookOutcome.DENY,
                "icp_too_small",
                f"Company below minimum size ({cfg.employee_count_min}).",
            )
        if employee_count > cfg.employee_count_max:
            return PlaybookDecision(
                PlaybookOutcome.DENY,
                "icp_too_large",
                f"Company above maximum size ({cfg.employee_count_max}).",
            )
        return PlaybookDecision(
            PlaybookOutcome.ALLOW,
            "icp_qualified",
            "Lead matches ICP.",
        )

    def evaluate_citations(self, *, sources_count: int) -> PlaybookDecision:
        minimum = self.config.outreach.required_citations_min
        if sources_count < minimum:
            return PlaybookDecision(
                PlaybookOutcome.DENY,
                "citation_insufficient",
                f"At least {minimum} research source(s) required before drafting.",
            )
        return PlaybookDecision(
            PlaybookOutcome.ALLOW,
            "citations_ok",
            "Research citations meet policy.",
        )

    def evaluate_stage_change(self, *, approved: bool, shadow_mode: bool) -> PlaybookDecision:
        cfg = self.config.pipeline
        if shadow_mode:
            return PlaybookDecision(
                PlaybookOutcome.REQUIRE_APPROVAL,
                "stage_shadow_dry_run",
                "Shadow mode: stage change recorded as dry-run only.",
            )
        if cfg.require_approval_for_stage_change and not approved:
            return PlaybookDecision(
                PlaybookOutcome.DENY,
                "stage_approval_required",
                "Manager or rep approval required before stage change.",
            )
        return PlaybookDecision(
            PlaybookOutcome.ALLOW,
            "stage_allowed",
            "Stage change permitted.",
        )
