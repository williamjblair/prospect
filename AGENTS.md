# AGENTS.md: Prospect (read this first)

You are continuing a hackathon build. **Active goal: complete and win the "Built with Claude:
Life Sciences" hackathon** (Anthropic + Gladstone + Cerebral Valley; Builder Track; remote; the
event window is Jul 7-13, 2026; New Work Only, i.e. code written during the event).

Full context, architecture, state, and strategy: **read [docs/HANDOFF.md](docs/HANDOFF.md).** It is
written for you.

## What Prospect is (one paragraph)

Prospect is a verified regulatory frontier of human CD4+ T-cell biology: a signed, content-addressed
graph of gene regulation re-derived from the released Marson CRISPRi Perturb-seq data, with no model
in the trust path. It exists to prove a thesis: generation got cheap, adjudication did not, so the
scarce thing is verified, replayable, human-accepted state. The receipt is the object that carries an
AI's activity across the boundary `Activity < Receipt < Proposal < Review < Verification < Accepted <
State`. See [docs/PROTOCOL.md](docs/PROTOCOL.md) for the reasoning.

- **Live:** https://prospect-sepia-six.vercel.app
- **Repo:** github.com/williamjblair/prospect (branch `master`)
- **Signed root:** `root_a8b0dcdd4024e12f` (re-derives with 0 drift)

## Golden rules (do not break these)

1. **New Work Only, and standalone.** No imports from or branding of Will's separate prior work. The
   receipt, frontier, and checkers are Prospect's own primitives, written for this event. Keep it
   standalone.
2. **No model in the trust path.** A model may propose, search, and draft. The verifier is frozen code
   over a frozen released table; acceptance is a human Ed25519 key. Never let a model move accepted state.
3. **Typed status, never "verified"/"true".** Findings that re-derive are `computationally_reproduced`;
   a hypothesis to test is `evidence_attached`; a disagreement is `contradicted`. Never launder weak
   evidence through strong language.
4. **Never say "verified" biology.** This proves the computation, never wet-lab or clinical truth.
5. **Writing: no em dashes, ever.** Restraint, concrete before abstract, no LLM-slop (no staccato
   aphorisms, no grandiosity). Use commas, colons, or periods. The repo is currently em-dash-free;
   keep it that way.
6. **Commits: no attribution footers.** No co-author trailers, generator bylines, or similar footer
   text. Those break a CLA.
7. **Secrets stay out of the repo and out of chat.** `ANTHROPIC_API_KEY` lives in gitignored `.env`
   (Will manages it). The signing key is gitignored `frontier/.prospect_signing_key`. Never print or
   commit either. Do not ask the user to paste keys.

## Run, verify, deploy

```bash
# one CLI for the whole loop (also: build|verify|sign|check|propose|agent|campaign|campaign-review|campaign-probe|campaign-triage|findings-index|judge-pack|receipt)
./prospect verify                   # re-derive 53k objects from frozen data, 0 drift (the gate)
python benchmark/mutation_pack.py   # the floor: zero tampered claim ever admitted
python tests/test_skill_parity.py   # the Skill checker matches the engine (112 claims, 0 drift)
./prospect campaign-probe           # Claude probes campaign rows, output remains proposal-only
./prospect campaign-triage          # turns probe disagreements into assay gates

# regenerate the frontier + site data after a data change:
python frontier/build.py && python frontier/verify.py && python frontier/sign.py --yes
python receipt/emit.py && cd web && python gen_data.py

# web app (Next.js 16 + Tailwind v4 + shadcn + sigma.js):
cd web && npm run build             # must pass; static export
cd web && vercel --prod --yes --scope constellate-dc388081   # deploy
```

The AI loops (`propose`, `agent`, the benchmark) need `ANTHROPIC_API_KEY` in `.env`. Default model
`claude-opus-4-8`. The web app reads one static `web/public/data/frontier.json`; it runs offline and
credential-free.

## Design

This is a **product** register (design serves the task). The design system is the Observatory
(cool first-light paper, indigo ink, one scarce kintsugi-gold accent, Hasui night-band dark mode).
Tokens in `web/app/globals.css`; system documented in [DESIGN.md](DESIGN.md) and [PRODUCT.md](PRODUCT.md).
Never raw hex; use tokens.

## Where the state is

Everything is committed and live. Nothing is mid-flight. Start from [docs/HANDOFF.md](docs/HANDOFF.md)
for the file map, what each phase shipped, the remaining opportunities, and the winning demo.
