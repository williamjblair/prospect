# Claude Science acceptance layer plan

## Objective

Make Prospect a judge-runnable acceptance layer for a real Claude Science export. The flow must show a reproducible associative signature entering through the Prospect connector, then a frozen Prospect causal checker returning typed verdicts with `accepted=false` and `human_signature_required`.

## Pre-registered causal typing rule

Input claim: each submitted signature gene is proposed as a causal regulator of the stimulated CD4+ activation program.

Prospect uses only `examples/data/marson_de_full.csv`.

- `evidence_attached`: the gene has on-target knockdown in `Stim8hr` and moves more than 10 transcripts.
- `contradicted`: the gene has on-target knockdown in `Stim8hr` and moves 10 or fewer transcripts.
- `not_assayed`: the gene is absent from the Marson table or lacks on-target knockdown in `Stim8hr`. This is not counted as a strong contradiction.

No verdict mutates accepted state. The bridge returns a proposal with the human key as the next step.

## Work plan

1. Commit the real Claude Science export fixture.
   - Copy `signature_genes.json`, `responder_DE_CD8.csv`, and `responder_DE_all.csv` from the local Claude Science artifact store.
   - Add a sanitized provenance manifest with source artifact ids, hashes, and the associative caveat.
   - Do not copy private onboarding artifacts or the report file that contains em dashes.

2. Build the deterministic claim typer.
   - Add a small module that reads a submitted gene list or DE table and emits per-gene typed causal verdicts.
   - Produce a compact demo packet for the web app and CLI.
   - Keep unsupported assay coverage distinct from contradiction.

3. Extend the MCP receipt bridge.
   - Keep existing receipt schema, validate, and submit tools intact.
   - Add a generic artifact submission tool for external producers.
   - Return `accepted=false`, `next=human_signature_required`, and typed verdict counts.

4. Add judge clients and tests.
   - Add a real Claude Science client command.
   - Add a second producer example using the same connector.
   - Test that the bridge exposes the new tool, admits no accepted state, and returns both `evidence_attached` and `contradicted` verdicts on the real export.

5. Surface the proof.
   - Generate web data containing the real artifact hashes, verdict counts, and commands.
   - Add an Overview headline panel above the discovery surfaces.
   - State the ceiling: computation over released data, not wet-lab or clinical truth.

6. Verify and commit.
   - Run the full Prospect gate.
   - Use the Browser plugin for local UI QA on a non-3000 port.
   - Commit locally. Do not push or deploy.
