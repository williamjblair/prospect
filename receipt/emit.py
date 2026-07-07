"""Emit Prospect Receipts from the frontier's findings and the agent's hypothesis: portable,
signed, evidence-bound proposals that record exactly how an AI's activity became (or is proposed
to become) accepted state. Nothing here re-derives biology; it repackages already-frozen state and
already-recorded activity into the receipt format, carrying the existing signatures.

  python receipt/emit.py     # writes receipts/*.json + receipts.jsonl
"""
from __future__ import annotations
import glob, hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from receipt.schema import Receipt, Artifact, EvidenceAtom, Verifier, Acceptance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "data")
FR = os.path.join(ROOT, "frontier")
OUTDIR = os.path.join(ROOT, "receipts")
FRONTIER_ID = "prospect_marson_cd4_perturbseq"

def _sha(path):
    if not os.path.exists(path):
        return "absent"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

def _artifact(name, rel, locator=""):
    return Artifact(name=name, sha256=_sha(os.path.join(ROOT, rel)), locator=locator or rel)

MARSON = _artifact("Marson CD4 DE table (classified)", "examples/data/atlas_backbone.json",
                   "s3://genome-scale-tcell-perturb-seq/marson2025_data/")
K562 = _artifact("Replogle K562 DE counts", "examples/data/replogle_k562_de.csv", "figshare:20029387")
RPE1 = _artifact("Replogle RPE1 DE counts", "examples/data/replogle_rpe1_de.csv", "figshare:20029387")
COLLECTRI = _artifact("CollecTRI regulons", "examples/data/collectri_human.csv", "omnipathdb.org")

def _root_acceptance():
    p = os.path.join(FR, "frontier.sig.json")
    if not os.path.exists(p):
        return None
    s = json.load(open(p))
    return Acceptance(signer=s.get("signer", ""), delta_id=s.get("root", ""),
                      pubkey=s.get("pubkey", ""), signature=s.get("signature", ""))

# --- evidence atoms per finding kind (verbatim numbers from the frozen verifier) --------------
def _finding_atoms(f):
    e, k = f["evidence"], f["kind"]
    A = lambda fact, val, src: EvidenceAtom(fact=fact, value=str(val), source=src)
    if k == "activation_module":
        ex = e.get("canonical_exemplar", {})
        top = sorted(ex.items(), key=lambda x: -x[1]["stim_max_de"])[:2]
        return [A(f"{g} is silent at rest, fires on stimulation", f"Rest {v['rest_de']} DE -> Stim {v['stim_max_de']} DE", "MarsonPerturbseqChecker") for g, v in top]
    if k == "regulator_vs_effector":
        pg = e.get("per_gene", {})
        picks = [g for g in ("PDCD1", "HAVCR2", "IL2") if g in pg][:3]
        return [A(f"{g} knockdown moves near-zero genes despite working KD", f"{pg[g]['n_de']} DE in {pg[g]['stim_condition']}", "MarsonPerturbseqChecker") for g in picks]
    if k == "essentiality_artifact":
        pg = e.get("per_gene", {})
        top = sorted(pg.items(), key=lambda x: -x[1]["rest_de"])[:2]
        return [A(f"{g} reshapes the transcriptome in a resting cell (housekeeping)", f"{v['rest_de']} DE at Rest", "MarsonPerturbseqChecker") for g, v in top]
    if k == "cross_cell_type_transfer":
        m = e.get("median_k562_de", {})
        return [A("essentiality artifacts replicate in non-immune K562", f"median {m.get('essentiality_artifact')} DE", "ReploglePerturbseqChecker"),
                A("the activation module stays inert in K562 (T-cell-specific)", f"median {m.get('activation_module')} DE", "ReploglePerturbseqChecker")]
    if k == "regulon_recovery":
        return [A("known CollecTRI targets are enriched among the genes each TF knockdown moved", f"{e.get('pooled_fold_enrichment')}x, Fisher p={e.get('combined_p')}", "frontier/regulon_recover.py"),
                A("Th1/Th2 master factors recovered from perturbation alone", "TBX21, GATA3", "hypergeometric test")]
    return []

def _finding_artifacts(kind):
    base = [MARSON]
    if kind == "cross_cell_type_transfer": base += [K562, RPE1]
    if kind == "regulon_recovery": base += [COLLECTRI]
    return base

def from_finding(f):
    kind = f["kind"]
    contested = kind in ("regulator_vs_effector",)
    return Receipt(
        frontier=FRONTIER_ID, claim=f["claim"], kind=kind, subject=f["genes"][:20],
        producer={"kind": "finding_producer", "model": None, "run": "frontier/findings.py"},
        artifacts=_finding_artifacts(kind), evidence=_finding_atoms(f),
        verifier=Verifier(name="frontier/verify.py", method="re-derives every object's content id from frozen fields; 0 drift = EXACT lane",
                          replay="./prospect verify"),
        status="contradicted" if contested else "computationally_reproduced",
        replayability="exact",
        scope=["holds in the released Marson CD4+ CRISPRi assay; not a wet-lab or clinical claim"],
        acceptance=_root_acceptance()).freeze()

def from_agent():
    p = os.path.join(DATA, "agent_run.json")
    if not os.path.exists(p):
        return None
    run = json.load(open(p)); h = run.get("hypothesis")
    if not h:
        return None
    sig = json.load(open(os.path.join(DATA, "agent_run.sig.json"))) if os.path.exists(os.path.join(DATA, "agent_run.sig.json")) else {}
    atoms = [EvidenceAtom(fact=e, value="frozen-data lookup", source="frozen-data tool") for e in h.get("evidence", [])]
    acc = Acceptance(signer=sig.get("signer", ""), delta_id=sig.get("delta_id", ""),
                     pubkey=sig.get("pubkey", ""), signature=sig.get("signature", "")) if sig else None
    return Receipt(
        frontier=FRONTIER_ID, claim=h["hypothesis"], kind="hypothesis", subject=[h["gene"]],
        producer={"kind": "autonomous_agent", "model": run["model"], "run": f"{run['tool_calls']} tool calls / {run['rounds']} rounds"},
        artifacts=[MARSON, K562, COLLECTRI],
        evidence=atoms,
        verifier=Verifier(name="frozen-data tools", method="every fact is a deterministic lookup against a released table; the agent cannot assert ungated biology",
                          replay="./prospect agent"),
        status="evidence_attached",   # the facts are replayable; the hypothesis is a proposal to test
        replayability="attested",     # the atoms replay exactly; the synthesis rests on a human's acceptance
        scope=[h.get("why_novel", ""), "a hypothesis to test, not an established result"],
        acceptance=acc).freeze()

def emit_all():
    findings = [json.loads(l) for l in open(os.path.join(FR, "findings.jsonl"))] if os.path.exists(os.path.join(FR, "findings.jsonl")) else []
    receipts = [from_finding(f) for f in findings]
    a = from_agent()
    if a:
        receipts.append(a)
    os.makedirs(OUTDIR, exist_ok=True)
    for r in receipts:
        json.dump(r.to_dict(), open(os.path.join(OUTDIR, r.receipt_id + ".json"), "w"), indent=2)
    with open(os.path.join(OUTDIR, "receipts.jsonl"), "w") as fh:
        for r in receipts:
            fh.write(json.dumps(r.to_dict()) + "\n")
    return receipts

def main(argv=None):
    import argparse
    from receipt.bridge import export_bridge, validate_receipt, DEFAULT_OUT
    ap = argparse.ArgumentParser(prog="prospect receipt")
    ap.add_argument("--no-bridge", action="store_true", help="skip bridge contract export")
    ap.add_argument("--bridge-out", default=str(DEFAULT_OUT), help="directory for bridge contract artifacts")
    args = ap.parse_args(argv)
    receipts = emit_all()
    print(f"emitted {len(receipts)} receipts -> {OUTDIR}/\n")
    for r in receipts:
        acc = f"signed by {r.acceptance.signer}" if r.acceptance else "unsigned"
        print(f"  {r.receipt_id}  {r.status:26s} {r.replayability:10s} {acc:22s} {r.kind}: {', '.join(r.subject[:3])}")
    if not args.no_bridge:
        bundle = export_bridge(args.bridge_out)
        errors = [e for r in bundle["receipts"] for e in validate_receipt(r)]
        if errors:
            raise SystemExit("receipt bridge validation failed: " + "; ".join(errors))
        print(f"\nexported receipt bridge -> {args.bridge_out}")

if __name__ == "__main__":
    main()
