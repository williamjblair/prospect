# Demo Script

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Clean deterministic run:

```bash
./prospect demo-mode --reset
```

## Two-Minute Version

**0:00, the problem.** Open Check. Say: every AI biology tool can produce a gene list. Prospect
tells you which genes are causal drivers. Reproducible is not verified.

**0:15, the wow.** Stay on the first screen. A real Claude Science Sade-Feldman melanoma ICB
signature enters Prospect. Claude Science preserved the artifact and its internal review completed.
Prospect asks the causal question the session leaves open: which signature genes move the activation
program when perturbed?

**0:40, the two verdicts.** Read the counts: 52 genes, 12 `evidence_attached`, 25
`associative_only`, 0 `contradicted`, 15 `not_assayed`. The signature is associative, so Prospect
does not manufacture contradictions. It separates candidate drivers from passengers and keeps
`accepted=false`.

**1:00, run your own claim.** Paste:

```text
IL7R
CCR7
PD-1
ENSG00000121410
NOTGENE
```

Copy the shareable result link. Point out the receipt id, typed verdicts, `accepted=false`, and
`human_signature_required`.

**1:25, why it matters.** Show the overclaiming number: 48% of confident AI major-regulator claims
are contradicted by the data, rising to 64% on famous checkpoints and cytokines.

**1:38, independent check.** Open Evidence. The locked 79-target comparison finds positive
cross-study agreement in perturbation reach (`rho=0.374`, permutation `P=0.0004`), and all three
adversarial kills pass. Different activation times keep it cross-context evidence, not equivalence.

**1:50, one honest lead.** Open Lead. PGGT1B is the hypothesis worth testing, not accepted biology:
prenylation mechanism, FNTA/RABGGTA partners, ChEMBL target, and a primary CD4+ CRISPRi experiment
that could refute it. A bounded registry audit found no direct comparable PGGT1B replication, so
the batch-specificity kill remains open.

Mention the corrective check: GSE278572 qualifies Prospect's own MED12 interpretation. High Rest
reach argues against activation specificity, but does not by itself establish housekeeping or
essentiality.

**1:58, trust boundary.** Open Receipts. The receipt bridge and MCP path submit proposals only.
Accepted records require frozen replay plus a human key. Close on root `root_a8b0dcdd4024e12f`.

## Commands To Mention

```bash
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python -m pytest tests/ -q
cd web && npm run typecheck && npm run build
./prospect claude-science
./prospect substrate-coverage
./prospect pggt1b-defended-evidence
python frontier/gse271788_calibration.py --check
./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service
python examples/claude_science_connector_client.py --url http://127.0.0.1:8130/mcp --json
python examples/prospect_connector_client.py --case openresearch --url http://127.0.0.1:8130/mcp --json
python receipt/replay_proposal.py <proposal.json-or-url>
python examples/claude_science_connector_client.py --json
python examples/receipt_bridge_client.py --json
```

Ceiling: computation over released data, not wet-lab or clinical truth.
