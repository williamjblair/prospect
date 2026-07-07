"""The three finding predicates, in one place, deterministic over the frozen backbone.

Every threshold here is a frozen, defensible cut derived from the released Marson
DE-stats table (examples/data/atlas_backbone.json). They are the definitions the
finding producer (frontier/findings.py) and the docs (docs/FINDINGS.md) share, so a
finding never drifts from the number that justifies it.

The biology that sets the thresholds:

  Raw DE count does NOT separate the essentiality artifact from the activation
  module: CD3E, LAT, PLCG1 each move 5,000+ genes at Stim8hr, the same magnitude as
  the SAGA/Mediator machinery. The discriminator is REACH AT REST. A gene that
  reorganizes the transcriptome in an *unstimulated* cell is doing housekeeping (or
  is essential); a gene that is silent at Rest and only fires after TCR engagement is
  activation-specific. On the released table the two classes fall on opposite sides of
  a wide empty gap:

      machinery (TADA2B, SGF29, MED12, ...)   Rest_DE  2,012 – 4,681
      activation module (CD3E, LAT, BCL10, ...) Rest_DE      1 – 7

  Phase 3 (cross-cell-type transfer, Replogle K562) tests this directly: the
  Rest-high genes should replicate in a non-immune cell (housekeeping); the
  activation module should not (immune-specific).
"""
from loop.find_surprises import CANON  # ~80 canonical CD4 T-cell genes

# --- frozen thresholds (see module docstring for the empirical gap that sets them) ---
REST_HIGH_DE = 1000   # Rest_DE above this = constitutive/essentiality reach (139 genes)
ACT_REST_MAX = 10     # activation module is ~silent at Rest
ACT_STIM_MIN = 100    # ...and a strong regulator once stimulated
EFFECTOR_DE_MAX = 3   # "near-zero" transcriptional change despite a working knockdown
NEVER_MAJOR_DE = 50   # a true effector is never a major regulator in ANY condition

STIM_CONDS = ("Stim8hr", "Stim48hr")


def _de(node, cond):
    return node["conditions"].get(cond, {}).get("n_de", 0)


def _rest_de(node):
    return _de(node, "Rest")


def _stim_max(node):
    return max((_de(node, c) for c in STIM_CONDS), default=0)


def _on_target(node, cond):
    return node["conditions"].get(cond, {}).get("kd") == "on-target KD"


def is_essentiality_artifact(node):
    """Constitutive high reach: moves the transcriptome even in a resting cell.
    Not a T-cell finding by itself - the reason naive effect-size ranking misleads."""
    return _rest_de(node) > REST_HIGH_DE


def is_activation_module(node):
    """Silent at Rest, strong regulator once stimulated, with a confirmed knockdown in
    the condition where it acts. The TCR-proximal program, recovered from perturbation."""
    if _rest_de(node) >= ACT_REST_MAX:
        return False
    for c in STIM_CONDS:
        if _de(node, c) > ACT_STIM_MIN and _on_target(node, c):
            return True
    return False


def effector_conditions(node):
    """Conditions where a canonical immune gene has a CONFIRMED on-target knockdown yet
    produces near-zero transcriptional change - an output of the program, not a driver.
    Returns the list of such conditions (empty if the gene is not a clean effector)."""
    if node["gene"] not in CANON:
        return []
    return [c for c in ("Rest",) + STIM_CONDS
            if _on_target(node, c) and _de(node, c) < EFFECTOR_DE_MAX]


def is_effector(node):
    return bool(effector_conditions(node))


def regulator_vs_effector(node):
    """Finding #2: a canonical immune gene the field treats as a regulator/target that
    stays near-silent EVEN UNDER STIMULATION despite a confirmed knockdown, and is never
    a major regulator in any condition. These are outputs of the program (checkpoints,
    cytokines), not transcriptional drivers. Scoped to stimulated conditions and gated on
    NEVER_MAJOR to exclude Rest-silent genes that are big regulators once stimulated
    (BCL10, ITK, LCP2 - those are finding #1, the activation module).

    Returns the stimulated conditions where the gene is a clean effector, or []."""
    if node["gene"] not in CANON:
        return []
    if _stim_max(node) >= NEVER_MAJOR_DE:
        return []
    return [c for c in STIM_CONDS if _on_target(node, c) and _de(node, c) < EFFECTOR_DE_MAX]


def is_regulator_vs_effector(node):
    return bool(regulator_vs_effector(node))


if __name__ == "__main__":
    import json, os
    bb = {n["gene"]: n for n in json.load(open(
        os.path.join(os.path.dirname(__file__), "..", "examples", "data", "atlas_backbone.json")))}
    ess = [g for g, n in bb.items() if is_essentiality_artifact(n)]
    act = [g for g, n in bb.items() if is_activation_module(n)]
    rve = [(g, regulator_vs_effector(n)) for g, n in bb.items() if is_regulator_vs_effector(n)]
    print(f"essentiality_artifact: {len(ess)} genes  e.g. {sorted(ess)[:8]}")
    print(f"activation_module:     {len(act)} genes  e.g. {sorted(act)[:8]}")
    print(f"regulator_vs_effector: {len(rve)} canonical genes")
    for g, cs in sorted(rve):
        n = bb[g]
        print(f"    {g:8s} effector in {str(cs):24s} (stim_max_DE={_stim_max(n)})")
