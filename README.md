# Prospect

A computationally reproduced regulatory frontier of human CD4+ T-cell biology.

Live: [prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Final submitter checklist: `docs/FINAL_SUBMISSION_CHECKLIST.md`

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

`prospect lab-pack` turns the top evidence-attached follow-ups into assay-ready rows for a
Gladstone-facing perturbation handoff: intervention, controls, readouts, exclusion criteria, and
public replay links. Every row remains proposal only. The condensed wet-lab handoff is
`docs/GLADSTONE_ASSAY_HANDOFF.md`.

`prospect campaign-review` adds the audit appendix for the 20-row campaign: lane counts, audit
questions, per-row decisions, and stop rules. It helps a judge inspect the leaderboard without
moving any row beyond proposal-only state.

`prospect campaign-probe` runs a Claude tool-use cross-examination against the top campaign rows,
then compares the model's recommendations to the deterministic review lanes. The output remains
proposal only; it shows where Claude pushes harder and where the frozen review stays conservative.

`prospect campaign-triage` converts those more-aggressive probe rows into assay gates: what would
have to pass before a conservative reviewer spends primary assay capacity.

`prospect campaign-gate-probe` pressure-tests those assay gates with closed recommendations:
`gate_sufficient`, `add_control`, or `lower_priority`. It remains proposal only.

Current public artifacts:

- `/data/frontier.json`
- `/data/judge_packet.json`
- `/data/receipt_bridge/receipt_manifest.json`
- `/data/pggt1b_matrix_slice.json`
- `/data/agent_campaign_review.json`
- `/data/campaign_agent_probe.json`
- `/data/campaign_triage.json`
- `/data/campaign_gate_probe.json`
- `/data/lab_packet.json`

## Run it

```bash
./prospect final-check            # run the submission gate
./prospect verify                 # re-derive every object from frozen data (EXACT lane, 0 drift)
./prospect check claims.json --data <released_table.csv>   # grade typed claims
./prospect propose --n 15         # Claude proposes; the frozen verifier decides
./prospect agent                  # autonomous agent: search → verify → converge on a hypothesis
./prospect receipt                # emit portable receipts (activity → signed replayable state)
./prospect mcp                    # expose the receipt bridge over MCP stdio
python examples/receipt_bridge_client.py # run the external receipt bridge client
./prospect campaign               # build the proposal-only campaign leaderboard
./prospect campaign-review        # build the campaign review appendix
./prospect campaign-probe         # run Claude probes against campaign rows
./prospect campaign-triage        # turn probe disagreements into assay gates
./prospect campaign-gate-probe    # pressure-test disagreement assay gates
./prospect pggt1b                 # build the PGGT1B evidence packet
./prospect lab-pack               # build the wet-lab assay packet
./prospect judge-pack             # build the judge packet manifest
./prospect sign                   # the human ceremony: accept the frontier root
python benchmark/mutation_pack.py # the floor: zero tampered claim is ever admitted
python tests/test_skill_parity.py # Skill checker matches the engine
python frontier/validation_sheet.py # write the wet-lab validation shortlist
```

The web app reads a single signed `frontier.json`; it runs credential-free and offline.

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
