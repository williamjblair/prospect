# Demo script

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Recording runbook: [DEMO_RECORDING_RUNBOOK.md](DEMO_RECORDING_RUNBOOK.md)

## Two-minute version

**0:00, acceptance layer.** Open Overview. Start on the first-screen arc. The claim is not that Prospect is another analysis notebook. It is the acceptance layer for AI-generated biology: activity enters as a receipt, Prospect replays it against frozen released data, and every result stays `accepted=false` until a human key accepts state.

**0:20, real Claude Science artifact.** Scroll to the Claude Science panel. A real Sade-Feldman melanoma ICB scRNA-seq signature enters Prospect. Claude Science preserved the artifact and its internal review completed with 0 findings. Prospect asks the causal question the session itself leaves open: which signature genes behave as drivers when perturbed? Result: 52 genes, 12 `evidence_attached`, 22 `associative_only`, 3 `contradicted`, 15 `not_assayed`. Frozen ORCS primary T-cell context shrinks uncovered genes to 5, still proposal-only.

**0:50, PGGT1B payload.** Return to the top arc, then Agent. PGGT1B is the hypothesis worth testing, not accepted biology. The novelty claim is downgraded: PubMed prior art already links PGGT1B or GGTase-I to T-cell localization and Treg programs. Prospect's narrower contribution is independent released-data support for a CD4 activation-transcriptome hypothesis, with ChEMBL compounds and a concrete primary CD4+ CRISPRi protocol.

**1:20, run your own claim.** Back to Overview. Paste `IL7R`, `CCR7`, `PD-1`, `ENSG00000121410`, and `NOTGENE`. The local web path returns a receipt-like state link with typed counts. The service path is one command: `./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service`.

**1:45, close.** Open Frontier. The MCP bridge exposes the same boundary. Claude can propose and external tools can submit, but accepted state remains frozen replay plus a human key. Close on the signed root `root_a8b0dcdd4024e12f` and the gate commands.

## Full walkthrough

1. Overview: first-screen arc, overclaiming counter, real Claude Science artifact, PGGT1B caveat, run-your-own path.
2. Overview: Claude Science panel, read both lanes. The internal artifact review can be clean while Prospect still separates causal drivers from passengers.
3. Overview: paste path, generate a shareable state link, and point to the service command plus `/ledger.json`.
4. Findings: the five signed finding objects, especially the famous checkpoint effector correction and cross-cell transfer.
5. Agent: PGGT1B dossier. Show novelty downgrade, PMIDs, STRING partners, ChEMBL target `CHEMBL4135`, and the wet-lab protocol.
6. Frontier: receipt bridge and MCP path. The bridge returns a proposal, never accepted state.

## Commands to show or mention

```bash
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
./prospect claude-science
./prospect substrate-coverage
./prospect pggt1b-defended-evidence
./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service
python examples/claude_science_connector_client.py --json
```

Ceiling: computation over released data, not wet-lab or clinical truth.
