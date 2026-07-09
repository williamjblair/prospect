# Demo Script

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Clean deterministic run:

```bash
./prospect demo-mode --reset
```

## Two-Minute Version

**0:00, the problem.** Open Overview. Say: every AI biology tool can produce a gene list. Prospect
tells you which genes are causal drivers. Reproducible is not verified.

**0:15, the wow.** Stay on the first screen. A real Claude Science Sade-Feldman melanoma ICB
signature enters Prospect. Claude Science preserved the artifact and its internal review completed.
Prospect asks the causal question the session leaves open: which signature genes move the activation
program when perturbed?

**0:40, the two verdicts.** Read the counts: 52 genes, 12 `evidence_attached`, 22
`associative_only`, 3 `contradicted`, 15 `not_assayed`. The signature is not called wrong. Prospect
separates drivers from passengers and keeps `accepted=false`.

**1:00, run your own claim.** Paste:

```text
IL7R
CCR7
PD-1
ENSG00000121410
NOTGENE
```

Copy the shareable state link. Point out the receipt id, typed verdicts, `accepted=false`, and
`human_signature_required`.

**1:25, why it matters.** Show the overclaiming number: 48% of confident AI major-regulator claims
are contradicted by the data, rising to 64% on famous checkpoints and cytokines.

**1:40, one honest lead.** Open Agent. PGGT1B is the hypothesis worth testing, not accepted biology:
prenylation mechanism, FNTA/RABGGTA partners, ChEMBL target, and a primary CD4+ CRISPRi experiment
that could refute it.

**1:55, trust boundary.** Open Frontier. The receipt bridge and MCP path submit proposals only.
Accepted state remains frozen replay plus a human key. Close on root `root_a8b0dcdd4024e12f`.

## Commands To Mention

```bash
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
./prospect claude-science
./prospect substrate-coverage
./prospect pggt1b-defended-evidence
./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service
python examples/claude_science_connector_client.py --json
python examples/receipt_bridge_client.py --json
```

Ceiling: computation over released data, not wet-lab or clinical truth.
