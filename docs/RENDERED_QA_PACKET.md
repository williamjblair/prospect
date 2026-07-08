# Prospect rendered QA packet

Production: [https://prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Local fallback: `http://localhost:8124`

Avoid local port: `3000`

## Manual browser checklist

This packet makes the final browser pass durable. It does not claim automated visual inspection.

## Viewports

| name | width | height |
|---|---:|---:|
| desktop | 1440 | 1000 |
| mobile | 390 | 844 |

## Tabs

| tab | must show | purpose |
|---|---|---|
| Overview | `Opening claim checks`, `48%`, `Judge packet` | Opening refusal, overclaim rate, and replay entry point. |
| Findings | `Scannable findings index`, `Substrate replay packet`, `MED19` | Scientific evidence path and protocol generalization. |
| Frontier | `Executable bridge path`, `accepted=false`, `human_signature_required` | Receipt boundary and no-model-in-trust-path behavior. |
| Agent | `Campaign pressure summary`, `Gladstone assay operations bundle`, `Gladstone pilot design`, `PGGT1B` | Claude pressure, proposal-only assay gates, pilot design, and lab handoff. |

## Evidence commands

- `./prospect final-check`
- `./prospect submit-smoke`
- `./prospect rendered-qa`

## Optional browser smoke

After starting the local web server on `8124`, run:

```bash
./prospect browser-qa --target both
```

This writes local evidence under ignored `output/playwright/`.

## Pass criteria

- No tab hides the signed root, typed status, or proposal-only boundaries.
- Overview opens on the refusal and overclaiming number, not decoration.
- Findings exposes the substrate replay path and MED19 contrast.
- Frontier shows receipt submission as proposal-only.
- Agent shows Claude pressure becoming assay gates and pilot design, not accepted state.
- Text fits at desktop and mobile viewport sizes.

This packet is a manual browser checklist. It does not prove wet-lab or clinical truth.

Rebuild:

```bash
./prospect rendered-qa
```
