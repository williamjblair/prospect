"""Typed claim + verdict schema. Claims are structured, never free-text-parsed
at verification time — extraction (LLM) is separate from checking (deterministic)."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, Literal

# What the natural-language sentence asserts, as typed fields.
@dataclass
class Claim:
    text: str                       # the original sentence (for the report)
    gene: str                       # perturbed gene symbol, e.g. "VAV1"
    condition: Optional[str] = None # "Rest" | "Stim8hr" | "Stim48hr" | None (unqualified)
    asserts_effect: bool = True     # claims the perturbation changes the transcriptome
    asserts_major: bool = False     # claims it's a "major"/"key" regulator (>10 DE genes)
    strength: Literal["quantitative", "promising_target", "mechanism", "clinical"] = "quantitative"

Status = Literal[
    "supported",            # data supports the quantitative claim (computationally reproduced)
    "refuted",             # data contradicts the claim
    "unsupported",          # perturbation didn't work / no effect — claim has no basis
    "needs_qualification",  # true only under a condition the claim didn't state
    "asserted",             # interpretive claim; not gradeable from this data (never "verified")
]

@dataclass
class Verdict:
    claim: Claim
    status: Status
    reason: str
    evidence: dict = field(default_factory=dict)   # the actual ground-truth cells
    mismatch_class: Optional[str] = None           # none | magnitude | no_knockdown | condition | fabricated

    @property
    def ok(self) -> bool:
        return self.status == "supported"

    def to_dict(self):
        d = asdict(self)
        return d
