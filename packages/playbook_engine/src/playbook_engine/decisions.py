from enum import StrEnum


class PlaybookOutcome(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class PlaybookDecision:
    __slots__ = ("outcome", "code", "message")

    def __init__(self, outcome: PlaybookOutcome, code: str, message: str) -> None:
        self.outcome = outcome
        self.code = code
        self.message = message

    @property
    def allowed(self) -> bool:
        return self.outcome in (PlaybookOutcome.ALLOW, PlaybookOutcome.REQUIRE_APPROVAL)

    def to_eval_label(self) -> str:
        if self.code.startswith("icp"):
            return "icp_qualified" if self.allowed else "icp_disqualified"
        if self.code.startswith("citation"):
            return "citations_ok" if self.allowed else "citations_insufficient"
        if self.code.startswith("stage"):
            return "stage_allowed" if self.allowed else "stage_denied"
        return self.code
