"""The Prospect Receipt: the portable object that carries an AI's activity across the boundary
into signed, replayable scientific state.

A model can assert anything in a second. A receipt is the structured proposal that says exactly
what was claimed, which frozen artifacts it stands on, which facts a verifier confirms, how to
replay it, what status the evidence actually earns, and whether a human accepted it. It is not a
truth object. It is the bridge from activity to state:

    Activity  <  Receipt  <  Proposal  <  Review  <  Verification  <  Accepted event  <  State

The receipt makes that boundary portable. Any producer of scientific activity, an agent, a
notebook, a pipeline, or Prospect's own loop, can emit one, and the same frozen gate decides what
becomes state. No step is silently skipped, and no model sits in the trust path: the verifier is
frozen and the acceptance is a human key. This is the general pattern Prospect is a working
instance of, written from scratch for this dataset.
"""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, field, asdict
from typing import Optional, Literal, List

# The typed status ladder. Never collapses to "verified"/"true". Weak evidence is never laundered
# through strong language: a hypothesis to test is `evidence_attached`, not `computationally_reproduced`.
Status = Literal[
    "claimed",                    # asserted, no evidence bound yet
    "evidence_attached",          # specific verified facts bound, but the claim itself is a proposal
    "computationally_reproduced", # re-derives from frozen released inputs (the EXACT lane)
    "independently_reanalyzed",   # a second, independent analysis agrees
    "contradicted",               # the data disagrees
    "refuted",                    # a stronger claim the data overturns
]

# How far the claim can be re-derived, and by whom.
Replayability = Literal[
    "exact",        # bit-for-bit re-derivable from frozen inputs (content-addressed)
    "reanalysis",   # re-run the analysis to reproduce
    "attested",     # rests on a human judgement or acceptance, not a re-derivation
    "none",
]

def content_id(frozen: dict) -> str:
    blob = "receipt\x1f" + json.dumps(frozen, sort_keys=True, separators=(",", ":"))
    return "rcpt_" + hashlib.sha256(blob.encode()).hexdigest()[:16]

@dataclass
class Artifact:
    name: str
    sha256: str                   # hash of the frozen input this receipt stands on
    locator: str = ""             # where to fetch it (path or public URI)

@dataclass
class EvidenceAtom:
    fact: str                     # the specific claim this atom supports
    value: str                    # the measured value, verbatim from the verifier
    source: str                   # which tool/table produced it

@dataclass
class Verifier:
    name: str                     # e.g. "MarsonPerturbseqChecker" / "frontier/verify.py"
    method: str                   # one line: how it decides
    replay: str                   # the command that re-derives the result

@dataclass
class Acceptance:
    signer: str
    delta_id: str
    pubkey: str
    signature: str

@dataclass
class Receipt:
    frontier: str                 # the frontier/dataset this proposes to change
    claim: str                    # the claim text
    kind: str                     # finding kind / "hypothesis" / "measurement"
    subject: List[str]            # the genes / entities
    producer: dict                # {kind, model, run} — the activity that generated it
    artifacts: List[Artifact]
    evidence: List[EvidenceAtom]
    verifier: Verifier
    status: Status
    replayability: Replayability
    scope: List[str] = field(default_factory=list)   # conditions, caveats
    acceptance: Optional[Acceptance] = None
    receipt_id: str = ""

    def freeze(self):
        self.receipt_id = content_id({
            "frontier": self.frontier, "claim": self.claim, "kind": self.kind,
            "subject": sorted(self.subject),
            "artifacts": sorted((a.name, a.sha256) for a in self.artifacts),
            "evidence": [(e.fact, e.value) for e in self.evidence],
            "verifier": self.verifier.name, "status": self.status,
            "replayability": self.replayability})
        return self

    def to_dict(self):
        d = asdict(self)
        d["accepted"] = self.acceptance is not None
        return d
