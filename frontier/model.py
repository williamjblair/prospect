"""The frontier data model: typed, content-addressed state for a verified regulatory
frontier. Nodes and edges are re-derivable from frozen released data (the EXACT lane);
every object carries a content_id = sha256 over its frozen fields. Contradictions and
open questions are first-class citable state. No status ever collapses to 'verified'/'true'.
"""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, asdict, field
from typing import Optional, Literal, List

DATASET = "marson2025_cd4_perturbseq"

def content_id(kind: str, frozen: dict) -> str:
    """Stable sha256 over the frozen, source-derived fields (sorted keys). Two builds from
    the same released table produce the same id — reproducibility, not a self-asserted stamp."""
    blob = kind + "\x1f" + json.dumps(frozen, sort_keys=True, separators=(",", ":"))
    return "cid_" + hashlib.sha256(blob.encode()).hexdigest()[:16]

# A gene's verified regulatory role. type is derived from the frozen table; status is the
# ladder (never 'verified'/'true').
NodeType = Literal["constitutive_regulator", "condition_specific_regulator",
                   "verified_non_regulator", "unverifiable_no_kd", "off_target"]
Status = Literal["established", "evidence_attached", "contradicted", "open"]

@dataclass
class Node:
    gene: str
    type: NodeType
    status: Status
    conditions: dict          # per-condition: {status, n_de, n_downstream, effect_size}
    out_degree: int = 0       # targets this gene regulates (edges out)
    in_degree: int = 0        # upstream regulators (edges in)
    dataset: str = DATASET
    cid: str = ""
    def freeze(self):
        self.cid = content_id("node", {"gene": self.gene, "type": self.type,
                                        "conditions": self.conditions, "dataset": self.dataset})
        return self

# A regulatory relationship: source knocked down -> target changes. direction/effect from the
# frozen released DE layers; never a live recompute.
@dataclass
class Edge:
    source: str
    target: str
    condition: str
    direction: Literal["up", "down"]     # sign(log_fc) of the target under source knockdown
    effect_size: float                    # log_fc
    q: float                              # adj_p_value
    kind: Literal["regulates", "rewires", "coregulates"] = "regulates"
    dataset: str = DATASET
    cid: str = ""
    def freeze(self):
        self.cid = content_id("edge", {"s": self.source, "t": self.target, "c": self.condition,
                                        "d": self.direction, "e": round(self.effect_size, 4),
                                        "q": round(self.q, 6), "k": self.kind, "dataset": self.dataset})
        return self

# Where a claimant (an AI model, or a literature reference) disagrees with the data. Kept as
# first-class terrain — never auto-adjudicated.
@dataclass
class Contradiction:
    subject: str                          # gene
    claimant: str                         # e.g. "claude-haiku-4-5" or "pmid:12345"
    claim: str
    data_verdict: str                     # refuted | unsupported
    reason: str
    status: Literal["contested"] = "contested"
    cid: str = ""
    def freeze(self):
        self.cid = content_id("contradiction", {"subject": self.subject, "claimant": self.claimant,
                                                 "claim": self.claim, "verdict": self.data_verdict})
        return self

# The frontier's demand surface: what the screen could not resolve.
@dataclass
class OpenQuestion:
    gene: str
    reason: Literal["no_knockdown", "untested"]
    status: Literal["open"] = "open"
    cid: str = ""
    def freeze(self):
        self.cid = content_id("open", {"gene": self.gene, "reason": self.reason})
        return self

# A mined, human-signable regulatory finding over a gene set. Deterministic from the frozen
# table via frontier/predicates.py; the evidence dict carries the per-gene numbers that justify
# it, so the finding and the number that supports it can never drift apart. See docs/FINDINGS.md.
FindingKind = Literal["activation_module", "regulator_vs_effector", "essentiality_artifact",
                      "cross_cell_type_transfer"]

@dataclass
class Finding:
    kind: FindingKind
    genes: List[str]                  # the gene set the finding is about
    claim: str                        # the one-line assertion (human-readable)
    evidence: dict                    # frozen backbone-derived support (thresholds + per-gene numbers)
    condition: Optional[str] = None
    status: Literal["established", "contested"] = "established"
    dataset: str = DATASET
    cid: str = ""
    def freeze(self):
        self.cid = content_id("finding", {"kind": self.kind, "genes": sorted(self.genes),
                                           "condition": self.condition, "evidence": self.evidence,
                                           "dataset": self.dataset})
        return self

def dump(objs, path):
    with open(path, "w") as fh:
        for o in objs:
            fh.write(json.dumps(asdict(o)) + "\n")
