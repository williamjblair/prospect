# Prospect

A computationally reproduced regulatory frontier of human CD4+ T-cell biology.

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

One-page judge handout: [docs/JUDGE_HANDOUT.md](docs/JUDGE_HANDOUT.md). Demo script: [docs/DEMO.md](docs/DEMO.md).

An AI can assert a claim about any gene in a second. Confirming it against the data takes
longer than most people spend, so overstated biology walks into slides, grants, and papers.
Prospect inverts that. It holds a linked graph of gene regulation where every node and edge is
re-derived from released CRISPRi Perturb-seq data and signed by a human. Nothing a model says
enters the graph on the model's word. You see what the data holds.

The dataset is the Marson lab's genome-scale CRISPRi Perturb-seq screen in primary human CD4+ T
cells: 11,526 genes classified, 37,106 gene-to-gene regulatory edges sliced from the released
matrix, contradictions and open questions kept as first-class terrain. Every object carries a
sha256 over its frozen source fields, so `prospect verify` re-derives the whole frontier from
scratch with zero drift, and `prospect sign` accepts a root hash with one Ed25519 signature. No
model sits in that path.

The deeper idea is a boundary: `Activity < Receipt < Proposal < Review < Verification < Accepted <
State`. Generation is cheap; replayable, human-accepted state is the scarce thing. A
**receipt** is the portable object that carries an AI's activity across that boundary, with a typed
status that never launders weak evidence as strong. See [docs/PROTOCOL.md](docs/PROTOCOL.md) for the
full reasoning.

## What the data says

Five findings, mined deterministically from the released table and signed into the frontier.
Full definitions and thresholds live in [docs/FINDINGS.md](docs/FINDINGS.md).

1. **The activation module, rebuilt from perturbation.** The TCR-proximal cascade (CD3D/E/G,
   LAT, LCP2, PLCG1, ITK, BCL10, MALT1) is inert in a resting cell and moves thousands of genes
   once stimulated. The screen recovers a textbook pathway from knockout effects alone, and the
   frontier types every edge as condition-gated.
2. **Regulator vs effector.** The genes the field targets most, PD-1, TIM-3, CTLA-4, LAG-3,
   IL-2, IFN-γ, change almost nothing on knockdown even under stimulation. They are outputs of
   the program, not its drivers. Each is a literature-vs-data contradiction, cited to the review
   that calls it a regulator.
3. **Reach is not regulation.** Rank genes by raw effect and the top of the list is SAGA and
   Mediator machinery, essentiality dressed as immunology. Reach at rest separates housekeeping
   from activation-specific control.
4. **Verifier transfer.** The same major-regulator claim, checked against a second Perturb-seq
   dataset in K562 (a non-immune line, Replogle 2022). Essentiality artifacts reshape the K562
   transcriptome too (median 71 DE genes); the activation module stays inert (median 4). The
   second dataset confirms the split with independent data.
5. **Regulon recovery.** Known CollecTRI targets are enriched among genes moved by each TF
   knockdown, with TBX21 and GATA3 recovered from perturbation alone.

## The overclaiming benchmark

Ask four frontier models, blind, to name major regulators, then check every claim against the
frozen table. On one 220-gene sample, **48% of confident "major regulator" claims are
contradicted** by the data. On the genes the field targets most, the overclaim rate is **64%**:
models overstate the famous checkpoints and cytokines more often than random genes. Generation
is cheap. The scarce thing is knowing which claims survive the data.

The same failure mode appears outside biology. OpenResearch, an alphaXiv project, has a public
report titled **"Adversarial falsification audit: 19 of 24 verification claims fail"**. It found
19 of 24 math verification claims false under exact-arithmetic re-derivation. Prospect does not
import that result into its biology frontier. It uses it as external context for the same boundary:
activity is not state, and accepted state needs frozen re-derivation plus a human key.

## The loop

`prospect propose` closes it. Claude proposes candidate regulators, the frozen verifier decides,
a human signs the accepted set. In one run Claude proposed fifteen well-argued transcription
factors; the data admitted six and rejected nine, including FOXP3, the textbook master regulator,
because its knockdown does not broadly reshape the transcriptome in this assay. Claude is genuinely
useful at proposing. The admission decision stays a deterministic re-derivation plus a human key.

`prospect mcp` makes the receipt boundary executable. An external workbench can discover the
receipt contract, validate a receipt, and submit it as a proposal. The response still says
`accepted: false`; accepted state requires the frozen verifier and the human signing path.
`python examples/receipt_bridge_client.py` runs that bridge as a tiny external client.

`prospect campaign` builds a proposal-only leaderboard of candidate regulators: ranked by
stimulated CD4+ effect, cell-type specificity, and distance from canonical effectors, every row
typed `evidence_attached` and none accepted. `prospect pggt1b` opens one row into a full evidence
packet, and `prospect disease-overlay` attaches frozen Open Targets disease context to the
leaderboard without moving any association into accepted state.

`prospect lab-pack` turns the top evidence-attached follow-ups into assay-ready rows: intervention,
controls, readouts, exclusion criteria, and public replay links. Every row remains proposal only,
ready for a wet lab to run and report back.

`prospect defended-discovery-endgame-result` is the stricter outcome pass. The corrected
pre-registration rests cell-type specificity on genome-wide K562 and treats sparse RPE1 coverage
as not_assayed context. Eighteen candidates were re-scored. PGGT1B clears the fixed bar as an
`evidence_attached` proposal with `accepted=false`; it remains the hypothesis worth testing, not
accepted biological state.

`prospect writeback` specifies the receipt that returns from that lab run: executed protocol, assay
readout, affected claims, reviewer signature, and state diff. A confirming or refuting result uses
the same shape. A contradiction is a new proposal, never a silent overwrite.

`prospect findings-index` builds a scannable index of the signed findings, and `prospect
judge-handout` emits a one-page handout with the live URL, signed root, five-minute path, trust
boundary, artifacts to open, and the actions that stay human-only.

Current public artifacts:

- `/data/frontier.json`
- `/data/finding_index.json`
- `/data/receipt_bridge/receipt_contract.json`
- `/data/receipt_bridge/receipt_manifest.json`
- `/data/receipt_bridge/receipt_bundle.json`
- `/data/claude_science_acceptance_demo.json`
- `/data/defended_discovery_endgame_preregistration.json`
- `/data/pggt1b_endgame_decision.json`
- `/data/defended_discovery_endgame_result.json`
- `/data/pggt1b_deep_dive.json`
- `/data/pggt1b_matrix_slice.json`
- `/data/agent_campaign.json`
- `/data/disease_genetics_overlay.json`
- `/data/lab_packet.json`
- `/data/lab_writeback_receipt.json`

## Run it

```bash
./prospect verify                 # re-derive every object from frozen data (EXACT lane, 0 drift)
./prospect sign                   # the human ceremony: accept the frontier root
./prospect check claims.json --data <released_table.csv>   # grade typed claims
./prospect propose --n 15         # Claude proposes; the frozen verifier decides
./prospect agent                  # autonomous agent: search, verify, converge on a hypothesis
./prospect receipt                # emit portable receipts (activity to signed replayable state)
./prospect mcp                    # expose the receipt bridge over MCP stdio
./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service # paste, HTTP, and MCP acceptance service
python examples/receipt_bridge_client.py # run the external receipt bridge client
./prospect campaign               # build the proposal-only campaign leaderboard
./prospect disease-overlay        # attach frozen Open Targets disease context to the leaderboard
./prospect pggt1b                 # build the PGGT1B evidence packet
./prospect lab-pack               # build the wet-lab assay packet
./prospect writeback              # build the lab return receipt shape
./prospect findings-index         # build the scannable finding index
./prospect judge-handout          # build the one-page judge handout
./prospect submit-pack            # print the copy-safe submission packet
./prospect build                  # rebuild the frontier from frozen data
python benchmark/mutation_pack.py # the floor: zero tampered claim is ever admitted
python tests/test_skill_parity.py # Skill checker matches the engine
```

The web app reads a single signed `frontier.json`; it runs credential-free and offline.
External teams can run their own signatures, DE tables, and gene lists through the service with
[docs/RUN_YOUR_OWN_CLAIM.md](docs/RUN_YOUR_OWN_CLAIM.md).

## Guarantees

- Deterministic findings from frozen released data, never a live DE recompute.
- Typed status only. The frontier never says "verified" or "true."
- Content-addressed and reproducible: `verify` re-derives 53k objects with zero drift.
- Human Ed25519 signature over the root. No model in any trust path.
- The mutation pack proves the floor: a tampered claim is never admitted as supported.
- The Skill ships a dependency-free checker; a parity test pins it to the engine, so the two
  copies cannot drift.
- The MCP bridge can validate and submit receipts only as proposals. A human key remains the only
  path into accepted state.

## Data

- Marson CD4+ T-cell CRISPRi Perturb-seq (Zhu, Dann, … Marson 2025), MIT-licensed:
  `s3://genome-scale-tcell-perturb-seq/marson2025_data/`
- Replogle genome-scale Perturb-seq, K562 (Replogle et al., Cell 2022, PMID 35688146), for the
  cross-cell-type transfer. Figshare article 20029387.

Ground-truth artifacts are frozen releases. The engine never re-runs a DE test.

## License

MIT. Built during Built with Claude: Life Sciences (Jul 7–13, 2026). See
[NEW_WORK.md](NEW_WORK.md).
