# Prospect frontier advancement memo

Audit date: July 8, 2026

Live project: https://prospect-sepia-six.vercel.app

Current signed root: `root_a8b0dcdd4024e12f`

Current repo state: use `git log -1 --oneline` as the source of truth.

## Active goal

Complete the next Prospect frontier-advancement campaign for the Built with Claude: Life Sciences
hackathon. The goal is no longer just submission readiness. The goal is to use the remaining window
through July 13, 2026 to attempt real, defensible discovery or protocol advancement between
released datasets, while preserving the existing green floor.

The work must stay Prospect-native:

- No prior-project branding, imports, or names.
- No model in the trust path.
- No accepted-state mutation from a model artifact.
- Status language remains `computationally_reproduced`, `evidence_attached`, and `contradicted`.
- Every data extension must name its frozen inputs, replay command, public artifact, and limitation.
- Every shipped slice must pass `./prospect final-check` and `./prospect submit-smoke`.

## Primary-source research

This memo is based on the current repo plus these source surfaces:

- Primary Human CD4+ T Cell Perturb-seq, Version v1.0, processed, released by the CZI Virtual Cells
  Platform on 22 Dec 2025: https://virtualcellmodels.cziscience.com/dataset/genome-scale-tcell-perturb-seq
- The Marson CD4+ source card describes genome-scale Perturb-seq across 22 million primary human
  CD4+ T cells, four donors, and three stimulation conditions: Rest, Stim8hr, Stim48hr.
- The same source card says the DE object `GWCD4i.DE_stats.h5ad` has one row per perturbation and
  condition, and the pseudobulk object contains donor, guide, and culture-condition fields.
- Replogle et al. 2022 processed Perturb-seq datasets on Figshare:
  https://plus.figshare.com/articles/dataset/_Mapping_information-rich_genotype-phenotype_landscapes_with_genome-scale_Perturb-seq_Replogle_et_al_2022_processed_Perturb-seq_datasets/20029387
- Replogle et al. 2022 includes K562 genome-scale Perturb-seq, K562 essential-scale Perturb-seq,
  and RPE1 essential-scale Perturb-seq, with AnnData single-cell and pseudobulk files.
- scPerturb: https://projects.sanderlab.org/scperturb/
- scPerturb is a harmonized resource of public single-cell perturbation datasets for benchmarking
  computational systems biology methods.
- PerturBase, Nucleic Acids Research 2025:
  https://academic.oup.com/nar/article/53/D1/D1099/7815638
- PerturBase reports 122 scPerturbation datasets from 46 public studies, including genetic and
  chemical perturbations, with search and analysis modules.
- Tahoe-100M, released through Tahoe and the Arc Virtual Cell Atlas:
  https://www.tahoebio.ai/news/open-sourcing-tahoe-100m
- Tahoe-100M reports 100 million single-cell data points, 60,000 drug-cell interactions, 50 cancer
  cell lines, and 1,200 drug perturbations.
- Open Targets Platform documentation: https://platform-docs.opentargets.org/
- Open Targets Platform aggregates target-disease evidence for target identification and exposes a
  GraphQL API and downloads.
- GWAS Catalog REST API documentation: https://www.ebi.ac.uk/gwas/rest/docs/api

Research conclusion: the strongest remaining hackathon work is not to ingest the largest possible
resource. It is to turn the existing Prospect checker into a sharper cross-dataset discovery
surface, then use larger resources only as scoped external evidence or scout packets.

## Reusable operating concepts, rewritten for Prospect

The useful prior operating concepts are method-level patterns, not names or code:

- Canonical state and projections are different. Prospect should treat the signed frontier, receipts,
  and frozen replay packets as canonical. Web JSON, docs, and screenshots are projections.
- A frontier extension is not a solved problem. A new replay packet can narrow uncertainty or expose
  a candidate, but it should say exactly what remains unaccepted.
- Activity ledgers are valuable only when a verifier can replay them. Claude traces, campaign probes,
  and assay gates should remain activity until converted into receipts or frozen packets.
- Caches are allowed only if their source and regeneration command are explicit. A large extracted
  table can be committed only when it is small, licensed, and reproducible, otherwise it stays in
  scratch with a downloader or extraction recipe.
- Fast gates beat broad confidence theater. Each workstream needs a focused verifier, then the full
  release gate before shipping.
- Visibility is part of state hygiene. If judges cannot find the replay object, receipt boundary, or
  status ladder in the app or public artifacts, the object is not useful for the hackathon.

## Current technical floor

Already shipped:

- Signed Marson frontier with root `root_a8b0dcdd4024e12f`.
- Five findings: activation module, regulator-vs-effector contradiction, essentiality artifact,
  cross-cell-type transfer, regulon recovery.
- Replogle K562 and RPE1 reduced DE-count tables.
- Substrate replay packet across Marson CD4+, Replogle K562, and Replogle RPE1.
- PGGT1B evidence packet and matrix slice.
- Twenty-row campaign leaderboard, all-row Claude probe, frozen probe audit, disagreement triage,
  full 11-of-11 gate probe, and pressure summary.
- Gladstone assay operations bundle and pilot design.
- Receipt bridge and external client.
- Final submission audit, release manifest, rendered QA packet, submit smoke, and final-check.

Do not weaken this floor for speculative discovery.

## Workstream 1: donor-condition replay

Priority: P0, highest scientific credibility per unit of risk.

Goal: split the aggregate Marson frontier by donor and condition so top candidates can be labeled
robust, donor-sensitive, or aggregate-only.

Why this matters: the current checker uses aggregate released DE results. The source dataset also
contains donor and culture-condition metadata in cell-level and pseudobulk AnnData files. A
Gladstone immunologist will trust PGGT1B and the campaign rows more if Prospect can say whether the
signal is donor-consistent or donor-fragile.

Data needed:

- `GWCD4i.pseudobulk_merged.h5ad`
- `GWCD4i.DE_stats.h5ad`
- Donor fields, guide fields, culture-condition fields, and keep-for-DE metadata from the released
  Marson objects.

Technical shape:

- Add `frontier/donor_replay.py`.
- Build a small artifact over the top five assay candidates plus the 20 campaign candidates.
- For each gene and condition, report donor availability, on-target guide support where available,
  and whether the aggregate call is supported by enough donor-level signal to be actionable.
- If donor-level DE cannot be reconstructed from the released objects in time, emit a bounded
  `evidence_attached` gap packet that names the missing statistic and exact source fields needed.

Potential discovery:

- A candidate that is aggregate-strong but donor-fragile becomes lower priority.
- A candidate that is aggregate-moderate but donor-consistent becomes a stronger assay candidate.
- PGGT1B may move from "large aggregate Stim8hr signal" to "robust across donors" or "needs donor
  stratification before acceptance."

Deliverables:

- `./prospect donor-replay`
- `examples/data/donor_condition_replay.json`
- `docs/DONOR_CONDITION_REPLAY.md`
- Optional `/data/donor_condition_replay.json` and an Agent tab summary if the packet is strong.

Status:

- Use `computationally_reproduced` only for statistics re-derived from released donor-level fields.
- Use `evidence_attached` for candidate prioritization.
- No accepted-state mutation.

Gate:

- Test packet schema, status, candidate count, no accepted-state mutation, and no model role.
- Add generated-artifact drift checks to `./prospect final-check`.
- Add public endpoint checks to `./prospect submit-smoke` only if surfaced in the app.

Go or no-go:

- Go if the donor fields are accessible without downloading a prohibitive object or re-running an
  unstable DE pipeline.
- No-go if donor replay requires a new statistical method that cannot be frozen and tested by July 13.

## Workstream 2: cross-substrate discovery

Priority: P0, shipped as the first frontier-advancement slice.

Current shipped surface: `./prospect cross-substrate-discovery` emits
`examples/data/cross_substrate_discovery.json`, [CROSS_SUBSTRATE_DISCOVERY.md](CROSS_SUBSTRATE_DISCOVERY.md),
and `/data/cross_substrate_discovery.json`. It classifies 11,526 Marson rows into 80 shared
cellular machinery rows, 409 T-cell-specific activation candidates, 333 non-immune-only effects,
and 10,704 ambiguous or not tested rows, with 20 campaign intersections headed by PGGT1B.

Goal: move beyond the current four exemplar rows and rank all overlapping genes by cross-substrate
class: shared cellular machinery, T-cell-specific activation, non-immune-only effect, and
ambiguous or not tested.

Why this matters: Prospect already shows that MED19 and BCL10 separate cleanly. The next step is a
full disagreement frontier over the overlapping Marson and Replogle gene universe, with ranked
surprises and assay implications.

Data available now:

- `examples/data/atlas_backbone.json`, 11,526 Marson genes with Rest, Stim8hr, and Stim48hr counts.
- `examples/data/replogle_k562_de.csv`, 9,867 K562 rows with DE counts.
- `examples/data/replogle_rpe1_de.csv`, 2,394 RPE1 rows with DE counts.

Technical shape:

- Add `frontier/cross_substrate_discovery.py`.
- For every overlapping gene, compute a deterministic class from frozen counts:
  - `shared_cellular_machinery`: high Rest or broad Marson signal plus broad K562 or RPE1 signal.
  - `t_cell_specific_activation`: low Rest, strong stimulated Marson signal, low K562 and RPE1 signal.
  - `non_immune_only_effect`: low Marson signal, high K562 or RPE1 signal.
  - `ambiguous_or_not_tested`: missing or mixed evidence.
- Rank rows by surprise score, not by model preference.
- Include candidate rows where the existing campaign ranking and cross-substrate class disagree.

Potential discovery:

- Non-canonical T-cell regulators with strong stimulated CD4+ signal and little non-immune transfer.
- Hidden housekeeping artifacts currently underweighted by Rest-only logic.
- Genes that look assay-ready until RPE1 or K562 exposes broad cellular machinery.

Deliverables:

- `./prospect cross-substrate-discovery`
- `examples/data/cross_substrate_discovery.json`
- `docs/CROSS_SUBSTRATE_DISCOVERY.md`
- `/data/cross_substrate_discovery.json`
- A compact campaign-intersection table in the Findings tab.

Status:

- The classification itself can be `computationally_reproduced`.
- Any biological interpretation stays `evidence_attached`.
- Rows can contradict campaign priority only as `contradicted` or `evidence_attached`, never as
  accepted biology.

Gate:

- Tests over exact counts for MED19, BCL10, PGGT1B, TADA2B, and at least one non-immune-only row.
- Tests for complete overlap accounting, closed class enum, and no accepted-state mutation.
- `./prospect final-check`.
- `./prospect submit-smoke` if public.

Go or no-go:

- Go immediately. The data is already committed and small.
- Stop before adding directionality or target-overlap unless the full Replogle AnnData files are
  available and the extraction can be frozen.

## Workstream 3: disease-genetics overlay

Priority: P1, high judge value if kept honest.

Goal: attach external immune-disease evidence to Prospect candidates without letting external
associations move accepted state.

Why this matters: the Marson source work is motivated by immune traits and disease genetics.
Gladstone judges will care whether a candidate such as PGGT1B, RCC1L, or RWDD2B has any independent
human genetics context. The key is to attach this as evidence, not proof.

Data sources:

- Open Targets Platform target-disease associations and genetics evidence.
- GWAS Catalog REST API for curated trait associations.
- Optional disease set: inflammatory bowel disease, rheumatoid arthritis, multiple sclerosis,
  type 1 diabetes, systemic lupus erythematosus, asthma, and allergic disease.

Technical shape:

- Add a small `external/disease_genetics.py` client or frozen fixture builder.
- Query only the top campaign and assay candidates.
- Cache the exact returned records, source, date, and query URL or GraphQL body.
- Produce a score-neutral overlay:
  - `has_external_association`
  - `association_source`
  - `disease_or_trait`
  - `evidence_type`
  - `why_it_matters`
  - `why_it_does_not_accept_state`

Potential discovery:

- A Prospect-only candidate with immune genetics support becomes a stronger wet-lab handoff.
- A strong perturbation candidate with no external genetics remains valuable but should be framed as
  cell-program discovery, not disease genetics.
- A famous immune target with genetics support but no perturbation effect becomes a clean example of
  claim separation.

Deliverables:

- `./prospect disease-overlay`
- `examples/data/disease_genetics_overlay.json`
- `docs/DISEASE_GENETICS_OVERLAY.md`
- Optional links from the PGGT1B and campaign packets.

Status:

- External association retrieval can be `evidence_attached`.
- Replayed local perturbation facts remain `computationally_reproduced`.
- No external API response can accept state.

Gate:

- Tests using frozen fixtures so CI does not depend on live APIs.
- Source and retrieval date in every row.
- Copy tests preventing therapeutic or clinical claims.
- `./prospect final-check`.

Go or no-go:

- Go only if the first query returns useful evidence for at least one candidate or a clear negative
  result worth showing.
- If the API work expands, freeze a small fixture and stop. Do not build a broad disease portal.

## Workstream 4: perturbation-atlas scout

Priority: P2, research scout, not a hackathon-critical implementation.

Goal: determine whether a larger perturbation corpus can provide one more credible replay substrate
before July 13.

Candidate sources:

- scPerturb, for harmonized public single-cell perturbation datasets.
- PerturBase, for a larger curated perturbation database with query and analysis modules.
- Tahoe-100M, for drug perturbation across many cancer cell lines.
- K562 Essential Perturb-seq Benchmark Dataset on the CZI Virtual Cells Platform, if a processed
  one-file benchmark is easier than the full Figshare set.

Technical shape:

- Build a `docs/PERTURBATION_ATLAS_SCOUT.md` first, not a data ingestion path.
- Score each candidate source on:
  - license
  - download size
  - API or direct data access
  - perturbation type
  - overlap with Prospect genes
  - ability to freeze a small replay table
  - risk of overclaiming
- Only ingest a dataset if it can yield a small frozen table with a deterministic checker in less
  than one work session.

Potential discovery:

- A third or fourth replay substrate that supports or contradicts campaign candidates.
- A drug-response contrast where a perturbation signature resembles a Prospect genetic perturbation,
  explicitly as hypothesis support only.

Deliverables:

- `docs/PERTURBATION_ATLAS_SCOUT.md`
- Optional `examples/data/perturbation_atlas_scout.json`
- Optional new checker only if source access is small and stable.

Status:

- Scout result is `evidence_attached`.
- Any small extracted table must be frozen and hashable before being used in a replay packet.

Gate:

- No public app surface unless the scout produces a real replay packet.
- `python tests/test_repo_hygiene.py`
- `./prospect final-check` for any committed generated artifact.

Go or no-go:

- Go for a scout memo.
- Do not ingest Tahoe-100M during the hackathon unless there is a small official subset with clear
  access and license fit. The source is scientifically exciting but too large for a rushed trust path.

## Workstream 5: campaign challenger ledger

Priority: P1 if more Claude budget is acceptable, otherwise P2.

Goal: convert additional model pressure into a challenger ledger rather than replacing the promoted
campaign probe.

Why this matters: the current all-20 probe is strong. The next Claude loop should ask a sharper
question: where would a skeptical model demote Prospect's top assay candidates after seeing the
cross-substrate and donor packets?

Technical shape:

- Keep the promoted campaign probe immutable.
- Add a challenger run under `/tmp` first.
- Compare challenger recommendations against:
  - deterministic campaign review
  - campaign probe
  - gate probe
  - donor replay, if shipped
  - cross-substrate discovery, if shipped
- Promote only if coverage is complete and the frozen audit has zero issues.

Potential discovery:

- A candidate that should be demoted because donor or substrate evidence is weak.
- A candidate that should be promoted into the five-row assay packet because cross-dataset evidence
  is cleaner than expected.

Deliverables:

- `./prospect campaign-challenger` only if needed.
- Otherwise, use existing `./prospect campaign-probe` and `./prospect campaign-probe-audit` with
  a new input packet.
- `examples/data/campaign_challenger_ledger.json`
- `docs/CAMPAIGN_CHALLENGER_LEDGER.md`

Status:

- Always `evidence_attached`.
- No accepted-state mutation.

Gate:

- Coverage audit.
- Rationale audit against frozen local facts.
- Complete requested versus returned gene list.
- `./prospect final-check`.

## Ranked execution plan

1. Run the floor: `./prospect final-check` and `./prospect submit-smoke`.
2. Build Workstream 2 first: cross-substrate discovery. It uses committed data and is the clearest
   route to real discovery between datasets.
3. Attempt Workstream 1 next: donor-condition replay. It is scientifically strongest if the source
   fields are accessible, but it may be blocked by data size or missing donor-level DE outputs.
4. Add Workstream 3 if source queries are clean: disease-genetics overlay for top candidates.
5. Write Workstream 4 scout memo if time remains. Ingest nothing large unless it can be frozen.
6. Run Workstream 5 only after cross-substrate or donor evidence changes the campaign ranking.
7. Refresh demo, submit packet, judge packet, release manifest, and web data after any public artifact.
8. Deploy only after web or public-data changes, using the deployment command in `AGENTS.md`.

## Definition of done for the new campaign

The new active goal is complete only when:

- The submission floor remains green.
- At least one new replay or scout artifact is shipped, or a source-backed no-go memo proves why it
  should not be shipped before July 13.
- The best available next discovery packet is public if it improves the demo.
- Every new artifact states status, trust boundary, source, replay command, and accepted-state effect.
- The campaign does not import or name prior-project code or branding.
- The final memo is current and names any human-only actions.
- `./prospect final-check` passes.
- `./prospect submit-smoke` passes after any public-surface change.

## Immediate recommendation

Build `cross-substrate discovery` first. It is the best combination of scientific credibility,
implementation feasibility, and hackathon story. It can discover genes where the current campaign
leaderboard and the independent K562/RPE1 replay disagree, without downloading new data or letting
Claude decide. If it produces even one clear demotion or promotion candidate, Prospect advances from
"we proved replay across datasets" to "we used replay across datasets to improve the frontier."
