# Prospect demo recording runbook

## Clean start

```bash
./prospect demo-mode --reset
```

Open the live or local site on Check. The local site should run on a port other than 3000.

## Two-minute storyboard

1. Check, first screen: Prospect is the acceptance layer for AI-generated biology. Reproducible activity is not accepted state.
2. Claude Science panel: a real scRNA-seq immunotherapy signature enters as a proposal. Show the exact split: 12 `evidence_attached`, 25 `associative_only`, 0 `contradicted`, and 15 `not_assayed`.
3. Run your own claim: paste `IL7R`, `CCR7`, `PD-1`, `ENSG00000121410`, and `NOTGENE`. Open the returned proposal page.
4. Evidence: show the 48% and 64% overclaiming benchmark, then the GSE278572 correction that qualifies Prospect's own MED12 interpretation.
5. Lead: PGGT1B is the proposal-only hypothesis worth testing, with prenylation mechanism, comparability limits, and a primary CD4+ CRISPRi refutation experiment.
6. Receipts: receipts cross the boundary, but accepted state waits for frozen replay and a human key.

## Five-minute extension

1. Open `/guide` on the acceptance service and show the paste path plus official Streamable HTTP MCP path.
2. Open `/ledger` after a submission with `publish_to_ledger=true` and show the self-declared producer plus typed counts.
3. Run `python examples/claude_science_connector_client.py --url <acceptance-service>/mcp --capture examples/data/claude_science_connector_run.json --json` and point to the same 52-gene typed breakdown plus the content-addressed call capture.
4. Run `python examples/prospect_connector_client.py --case openresearch --url <acceptance-service>/mcp --json` to show a second producer using the same evaluator.
5. Run the returned `python receipt/replay_proposal.py <proposal-url>.json` command to re-derive the receipt identity and typed verdicts.
6. Close on `root_a8b0dcdd4024e12f`, `accepted=false`, and the human-only acceptance step.

## Live Claude Science call

Use a writable `OPERON` session with the registered `prospect` connector and the real
`signature_genes.json` export. Keep connector approvals on. Send one bounded instruction:

```text
Submit the attached signature through prospect.acceptance.submit_artifact as an
associative_signature from claude_science_sade_feldman. Set publish_to_ledger=false.
Do not accept or sign anything. Return the proposal id, receipt id, typed-status counts,
proposal URL, and replay command exactly as returned by Prospect.
```

Approve only the Prospect submission tool. Capture the tool call and returned proposal. The expected
split is 12 `evidence_attached`, 25 `associative_only`, 0 `contradicted`, and 15 `not_assayed`.
Stop if the returned receipt or verdicts differ from the checked-in connector capture.

## Fixture fallback

If the live Claude Science instance is unavailable, use the checked-in real export fixture under `examples/data/claude_science_real_export/` and the packet at `examples/data/claude_science_acceptance_demo.json`. Label it as a real export fixture, not a live session.
