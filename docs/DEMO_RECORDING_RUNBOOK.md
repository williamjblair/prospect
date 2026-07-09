# Prospect demo recording runbook

## Clean start

```bash
./prospect demo-mode --reset
```

Open the live or local site on Overview. The local site should run on a port other than 3000.

## Two-minute storyboard

1. Overview, first screen: Prospect is the acceptance layer for AI-generated biology. Reproducible activity is not accepted state.
2. Traceable headline rail: show that the overclaim, real artifact, PGGT1B, and funnel numbers each have an artifact and command.
3. Claude Science panel: a real scRNA-seq immunotherapy signature enters as a proposal. Prospect separates drivers, passengers, contradicted driver claims, and not_assayed genes.
4. Run your own claim: paste `IL7R`, `CCR7`, `PD-1`, `ENSG00000121410`, and `NOTGENE`. Open the returned state page.
5. Agent tab: PGGT1B is the proposal-only hypothesis worth testing, with prenylation mechanism, prior-art downgrade, and a primary CD4+ CRISPRi refutation experiment.
6. Frontier tab: receipts cross the boundary, but accepted state waits for frozen replay and a human key.

## Five-minute extension

1. Open `/guide` on the acceptance service and show the paste path plus MCP path.
2. Open `/ledger` after the demo submission and show producer attribution plus typed counts.
3. Run `python examples/claude_science_connector_client.py --json` and point to the same 52-gene typed breakdown.
4. Run `python examples/prospect_connector_client.py --case openresearch --json` to show a second producer using the same connector.
5. Close on `root_a8b0dcdd4024e12f`, `accepted=false`, and the human-only acceptance step.

## Fixture fallback

If the live Claude Science instance is unavailable, use the checked-in real export fixture under `examples/data/claude_science_real_export/` and the packet at `examples/data/claude_science_acceptance_demo.json`. Label it as a real export fixture, not a live session.
