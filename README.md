# Prospect

The tool that tells a biologist which genes in an AI prediction list behave as causal drivers.

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Demo script: [docs/DEMO.md](docs/DEMO.md). Judge handout: [docs/JUDGE_HANDOUT.md](docs/JUDGE_HANDOUT.md).

Every AI biology tool can produce a signature, gene list, or differential-expression table. Prospect
checks that activity against frozen perturbation data and returns typed verdicts: `evidence_attached`
for causal-driver evidence, `associative_only` for passengers, `contradicted` for refuted driver
claims, and `not_assayed` for genes the table cannot test. Reproducible is not verified. Every
submission stays `accepted=false` until a frozen replay and a human key accept the record.

The payload is primary human CD4+ T-cell activation. Prospect replays claims against the released
Marson CRISPRi Perturb-seq screen, a frozen CD4+ evidence graph with 11,526 genes, 37,106 regulatory
edges, five CD4+ findings, and root `root_a8b0dcdd4024e12f`. No model is in the trust path.

## What A Judge Sees

1. A real Claude Science scRNA-seq immunotherapy signature enters Prospect.
2. Claude Science preserves the artifact and its internal review completes.
3. Prospect asks the causal question: which signature genes move the activation program when perturbed?
4. Because the export is associative, the result is 12 `evidence_attached`, 25 `associative_only`,
   0 `contradicted`, and 15 `not_assayed`.
5. A judge can switch to an explicit causal claim. Only a comparable refuted driver claim can earn
   `contradicted`.
6. A pasted input receives the same receipt and verdicts through Python, HTTP, stdio MCP, or hosted MCP.

Prospect frames the signature as associative and separates drivers from passengers, which is exactly
what an associative signature needs before it can become a biological claim.

## The Sharp Evidence

- **AI overclaiming:** 48% of confident major-regulator claims are contradicted by the measured data,
  rising to 64% on famous checkpoints and cytokines.
- **Real Claude Science artifact:** 52 genes typed as drivers, passengers, contradicted driver claims,
  or not assayed against frozen Marson perturbation data.
- **PGGT1B:** one mechanism-first hypothesis worth testing, not accepted biology. The kept claim is a
  narrow CD4 activation-transcriptome hypothesis with prenylation partners, ChEMBL context, and a
  falsifiable primary CD4+ CRISPRi experiment.
- **MED12 correction:** an independently frozen GSE278572 comparison qualifies Prospect's own
  interpretation. High resting reach is evidence against activation specificity, but is not enough
  to call a gene housekeeping or an essentiality artifact.
- **Signed evidence graph:** five deterministic CD4+ findings recover known activation biology, separate
  effectors from drivers, catch essentiality artifacts, transfer the checker to K562, and recover
  CollecTRI regulons.
- **Receipt bridge:** any external workbench can submit a receipt through the MCP bridge. The bridge
  returns a proposal with `accepted=false`; an accepted record requires a human key.

## Public Artifacts

- `/data/check.json`
- `/data/frontier.json`
- `/data/claude_science_acceptance_demo.json`
- `/data/gse278572_comparator.json`
- `/data/pggt1b_defended_evidence.json`
- `/data/finding_index.json`
- `/data/overclaim_counter.json`
- `/data/receipt_bridge/receipt_contract.json`
- `/data/receipt_bridge/receipt_manifest.json`
- `/data/receipt_bridge/receipt_bundle.json`

## Run It

```bash
./prospect verify
python benchmark/mutation_pack.py
python tests/test_skill_parity.py
python tests/test_marson.py
python -m pytest tests/ -q
cd web && npm run typecheck && npm run build
./prospect demo-mode --reset
./prospect claude-science
./prospect substrate-coverage
./prospect pggt1b-defended-evidence
./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service
python examples/receipt_bridge_client.py --json
python examples/claude_science_connector_client.py --json
```

## Guarantees

- Frozen released data, never a live differential-expression recompute.
- Typed status only, no wet-lab or clinical truth claim.
- Content-addressed replay: `./prospect verify` re-derives 53k objects with zero drift.
- Human Ed25519 signature over accepted records. No model makes the final call.
- Mutation pack floor: zero tampered claim is admitted.
- MCP bridge and acceptance service submit proposals only.
- `prospect.receipt.v1` binds the complete proposal body. Acceptance is a separate event.

## Data

- Marson CD4+ T-cell CRISPRi Perturb-seq, Zhu, Dann, Marson 2025.
- Replogle genome-scale Perturb-seq, K562 and RPE1, Replogle et al. Cell 2022, PMID 35688146.
- CollecTRI regulons and frozen public context used only as evidence, never as automatic acceptance.

## License

MIT. Built during Built with Claude: Life Sciences, Jul 7 to 13, 2026. See [NEW_WORK.md](NEW_WORK.md).
