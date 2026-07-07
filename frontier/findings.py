"""Mint the three findings (docs/FINDINGS.md) as content-addressed, human-signable objects,
deterministically from the frozen backbone via frontier/predicates.py. Each Finding carries the
per-gene numbers that justify it in its `evidence` dict, so the claim and its support are hashed
together and cannot drift.

Also mints the literature-vs-data Contradictions for finding #2: each cited effector gene becomes
a Contradiction whose claimant is the PMID that calls it a regulator/target and whose data_verdict
is the near-zero DE count that refutes that reading in this assay.

  python frontier/findings.py     # writes frontier/findings.jsonl
"""
from __future__ import annotations
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frontier.model import Finding, Contradiction, dump
from frontier import predicates as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "data")
FR = os.path.join(ROOT, "frontier")

def _load_backbone():
    return {n["gene"]: n for n in json.load(open(os.path.join(DATA, "atlas_backbone.json")))}

def _rest(n): return P._de(n, "Rest")
def _stim_max(n): return P._stim_max(n)


def build_findings(bb):
    """Return the three Findings, deterministic over the backbone dict {gene: node}."""
    findings = []

    # --- Finding 1: the activation module (silent at Rest, strong once stimulated) ---
    act = sorted(g for g, n in bb.items() if P.is_activation_module(n))
    # the canonical exemplar: TCR-cascade / CANON genes among the activation module
    act_canon = sorted(g for g in act if g in P.CANON)
    exemplar = {g: {"rest_de": _rest(bb[g]), "stim_max_de": _stim_max(bb[g])} for g in act_canon}
    findings.append(Finding(
        kind="activation_module",
        genes=act,
        claim=("The TCR-proximal signaling cascade is silent in a resting cell and becomes the "
               "regulatory core of the transcriptome only after stimulation. The screen recovers "
               "this module from knockout effects with no prior pathway knowledge."),
        evidence={"n_genes": len(act),
                  "thresholds": {"rest_de_max": P.ACT_REST_MAX, "stim_de_min": P.ACT_STIM_MIN},
                  "canonical_exemplar": exemplar},
        status="established").freeze())

    # --- Finding 2: regulator vs effector (canonical genes, worked KD, ~0 DE under stim) ---
    eff = {g: P.regulator_vs_effector(n) for g, n in bb.items() if P.is_regulator_vs_effector(n)}
    eff_ev = {}
    for g, conds in sorted(eff.items()):
        c = conds[0]
        eff_ev[g] = {"stim_condition": c, "n_de": P._de(bb[g], c), "stim_max_de": _stim_max(bb[g])}
    findings.append(Finding(
        kind="regulator_vs_effector",
        genes=sorted(eff),
        claim=("The T-cell genes the field targets most (immune checkpoints and effector cytokines) "
               "produce near-zero transcriptional change when knocked down, even under stimulation. "
               "They are outputs of the T-cell program, not its transcriptional drivers."),
        evidence={"n_genes": len(eff),
                  "thresholds": {"effector_de_max": P.EFFECTOR_DE_MAX, "never_major_de": P.NEVER_MAJOR_DE},
                  "per_gene": eff_ev},
        status="contested").freeze())

    # --- Finding 3: reach is not regulation (constitutive high Rest reach = essentiality) ---
    ess = sorted(g for g, n in bb.items() if P.is_essentiality_artifact(n))
    ess_ev = {g: {"rest_de": _rest(bb[g])} for g in ess}
    act_rest_ceiling = max((_rest(bb[g]) for g in act), default=0)
    findings.append(Finding(
        kind="essentiality_artifact",
        genes=ess,
        claim=("Ranking genes by raw transcriptional reach surfaces the cell's general machinery "
               "(SAGA, Mediator), not its immune biology. Reach at Rest separates housekeeping from "
               "activation-specific regulation. Cross-cell-type transfer (Replogle) tests this."),
        evidence={"n_genes": len(ess),
                  "thresholds": {"rest_de_min": P.REST_HIGH_DE},
                  "gap": {"machinery_rest_de_min": min((v["rest_de"] for v in ess_ev.values()), default=0),
                          "activation_module_rest_de_max": act_rest_ceiling},
                  "per_gene": ess_ev},
        status="established").freeze())

    return findings


def literature_contradictions(bb):
    """One Contradiction per cited finding-#2 gene: PMID claimant vs the released DE count."""
    cites = json.load(open(os.path.join(DATA, "literature_citations.json")))["citations"]
    out = []
    for gene, meta in sorted(cites.items()):
        n = bb.get(gene)
        if not n:
            continue
        conds = P.regulator_vs_effector(n)
        if not conds:
            continue  # only cite genes the data actually shows as effectors
        c = conds[0]
        n_de = P._de(n, c)
        out.append(Contradiction(
            subject=gene,
            claimant=f"pmid:{meta['pmid']}",
            claim=meta["canonical_role"],
            data_verdict="refuted",
            reason=(f"Confirmed on-target knockdown in {c}, but only {n_de} genes changed "
                    f"(<{P.EFFECTOR_DE_MAX}). An effector/output of the program, not a "
                    f"transcriptional regulator in this assay. Lit: {meta['first_author']}, "
                    f"{meta['journal']} {meta['year']} (doi:{meta['doi']}).")).freeze())
    return out


def main():
    bb = _load_backbone()
    findings = build_findings(bb)
    dump(findings, os.path.join(FR, "findings.jsonl"))
    lit = literature_contradictions(bb)
    for f in findings:
        print(f"  {f.kind:24s} {len(f.genes):4d} genes · status={f.status} · {f.cid}")
    print(f"  literature contradictions: {len(lit)} "
          f"({', '.join(c.subject for c in lit)})")
    return findings, lit

if __name__ == "__main__":
    main()
