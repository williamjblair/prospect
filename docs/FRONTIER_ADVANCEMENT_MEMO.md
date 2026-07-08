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
- scPerturb RNA and protein H5AD archive on Figshare:
  https://plus.figshare.com/articles/dataset/scPerturb_Single-Cell_Perturbation_Data_RNA_and_protein_h5ad_files/24160713
- The scPerturb archive is a 25.01 GB harmonized collection, useful as a future corpus but too broad
  for a rushed accepted-state boundary.
- PerturBase, Nucleic Acids Research 2025:
  https://academic.oup.com/nar/article/53/D1/D1099/7815638
- PerturBase reports 122 scPerturbation datasets from 46 public studies, including genetic and
  chemical perturbations, with search and analysis modules.
- Tahoe-100M, released through Tahoe and the Arc Virtual Cell Atlas:
  https://arcinstitute.org/news/arc-vevo
- Tahoe-100M reports 100 million single-cell data points, 60,000 drug-cell interactions, 50 cancer
  cell lines, and 1,200 drug perturbations.
- CZI K562 Essential Perturb-seq Benchmark Dataset:
  https://virtualcellmodels.cziscience.com/dataset/k562-essential-perturb-seq
- The CZI K562 benchmark is the most compact future replay candidate, but it overlaps the already
  shipped Replogle K562 substrate and needs license review before any committed extract.
- pertpy Replogle 2022 K562 GWPS loader:
  https://pertpy.readthedocs.io/en/stable/api/data/pertpy.data.replogle_2022_k562_gwps.html
- The pertpy loader is useful tooling, but it points back to a substrate Prospect already reduced.
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

Priority: P0, shipped.

Goal: split the aggregate Marson frontier by donor and condition so top candidates can be labeled
robust, donor-sensitive, or aggregate-only.

Why this matters: the current checker uses aggregate released DE results. The source dataset also
contains donor and culture-condition metadata in cell-level and pseudobulk AnnData files. A
Gladstone immunologist will trust PGGT1B and the campaign rows more if Prospect can say whether the
signal is donor-consistent or donor-fragile.

Current shipped surface: `./prospect donor-replay` emits
`examples/data/donor_condition_replay.json`, [DONOR_CONDITION_REPLAY.md](DONOR_CONDITION_REPLAY.md),
and `/data/donor_condition_replay.json`. The packet replays the 20 campaign rows against a frozen,
small source extract from `GWCD4i.DE_stats.h5ad`. It uses donor-correlation and guide-support fields
from the released object, not a new DE recompute.

Source fields:

- `GWCD4i.DE_stats.h5ad`
- `donor_correlation_hits_min`
- `donor_correlation_hits_mean`
- `donor_correlation_all_min`
- `donor_correlation_all_mean`
- `n_guides`
- `single_guide_estimate`
- `guide_n_signif_ontarget`
- released aggregate DE counts from the frozen Prospect table

Classification:

- `donor_supported`: at least 50 aggregate DE genes, at least two guides, hits-min at least 0.5,
  and hits-mean at least 0.6.
- `donor_fragile`: at least 50 aggregate DE genes but hits-min below 0.35.
- `guide_limited`: single-guide estimate or fewer than two guides.
- `donor_intermediate`: aggregate signal with donor statistics that do not meet the supported or
  fragile thresholds.

Current result:

- 20 campaign rows replayed.
- 13 donor-supported rows.
- 2 donor-intermediate rows.
- 4 donor-fragile rows.
- 1 guide-limited row.
- PGGT1B is donor-supported in Stim8hr: 3,014 aggregate DE genes, 2 guides,
  `donor_correlation_hits_min` 0.6045, and `donor_correlation_hits_mean` 0.7185.
- RWDD2B, IRF4, and two other rows are donor-fragile under the frozen threshold.
- SNAP29 is guide-limited.

Discovery value:

- The top assay-design row, PGGT1B, is no longer just a large aggregate Stim8hr signal. It is a
  donor-supported campaign row under the released donor-correlation fields.
- Donor-fragile rows are demoted into capacity-sensitive or control-heavy lanes before wet-lab
  handoff.
- The packet gives judges a concrete example of frontier advancement inside the Marson dataset,
  not just protocol presentation.

Deliverables:

- `./prospect donor-replay`
- `examples/data/donor_condition_replay.json`
- `examples/data/donor_condition_source_rows.json`
- `docs/DONOR_CONDITION_REPLAY.md`
- `/data/donor_condition_replay.json`
- Agent tab summary in the live app

Status:

- Packet status is `computationally_reproduced`.
- Candidate prioritization remains `evidence_attached`.
- No accepted-state mutation.

Gate:

- Tests cover packet schema, status, thresholds, row count, PGGT1B classification, no accepted-state
  mutation, no model role, no forbidden status language, and UI contract.
- `./prospect final-check` drift-checks the donor source extract, packet, doc, and public JSON.
- `./prospect submit-smoke` checks the public endpoint.

Limitations:

- This is not donor-level wet-lab replication.
- It does not recompute per-donor DE.
- It does not move any row into accepted biological state.

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

Priority: P1, shipped.

Goal: attach external immune-disease evidence to Prospect candidates without letting external
associations move accepted state.

Why this matters: the Marson source work is motivated by immune traits and disease genetics.
Gladstone judges will care whether a candidate such as PGGT1B, RCC1L, or RWDD2B has any independent
human genetics context. The key is to attach this as evidence, not proof.

Current shipped surface: `./prospect disease-overlay` emits
`examples/data/disease_genetics_overlay.json`, [DISEASE_GENETICS_OVERLAY.md](DISEASE_GENETICS_OVERLAY.md),
and `/data/disease_genetics_overlay.json`. The packet queries Open Targets once, freezes a small
source extract, and normally replays from the committed extract.

Source:

- Open Targets Platform GraphQL API, target search plus `target.associatedDiseases`.
- Query scope: the 20 campaign rows only.
- Page size: 120 associations per target.
- Selection filter: immune or hematologic terms with Open Targets association score at least 0.05.
- GWAS Catalog REST v2 was probed by campaign gene, but the bounded immune-trait filter did not add
  useful rows, so it is not part of the shipped packet.

Current result:

- 20 campaign rows overlaid.
- 20 rows have Open Targets target-disease associations.
- 10 rows have selected immune or hematologic context.
- 4 rows have selected immune or hematologic genetic context.
- PGGT1B has psoriasis context, literature only under this extract.
- CCDC22, SCO2, GZMB, and IRF4 have selected genetic-context rows.
- Rows without selected immune or hematologic context remain perturbation-first candidates, not
  disease-genetics claims.

Discovery value:

- The packet separates "strong perturbation candidate" from "candidate with external disease
  context" without letting either claim swallow the other.
- PGGT1B remains a strong donor-supported perturbation candidate, but the overlay keeps its external
  disease context modest and non-genetic.
- CCDC22, GZMB, and IRF4 become useful comparison rows for assay framing because their external
  context is stronger than their status in Prospect's accepted state.

Deliverables:

- `./prospect disease-overlay`
- `examples/data/disease_genetics_source_rows.json`
- `examples/data/disease_genetics_overlay.json`
- `docs/DISEASE_GENETICS_OVERLAY.md`
- `/data/disease_genetics_overlay.json`
- Agent tab summary in the live app

Status:

- External association retrieval is `evidence_attached`.
- Replayed local perturbation facts remain `computationally_reproduced`.
- No external API response can accept state.

Gate:

- Tests use the frozen extract so CI does not depend on live APIs.
- Source, endpoint, retrieval date, and regeneration command are in the packet.
- Copy tests prevent strong status language and clinical-truth claims.
- `./prospect final-check`.

Limitations:

- This is not a disease-causality claim.
- It is not a target-prioritization score.
- It does not prove wet-lab, therapeutic, or clinical results.

## Workstream 4: perturbation-atlas scout

Priority: P2, shipped as a research scout and no-go memo.

Goal: determine whether a larger perturbation corpus can provide one more credible replay substrate
before July 13.

Current shipped surface: `./prospect perturbation-scout` emits
`examples/data/perturbation_atlas_scout.json` and
[PERTURBATION_ATLAS_SCOUT.md](PERTURBATION_ATLAS_SCOUT.md). It does not add a public endpoint because
it intentionally ingests no new biological substrate.

Candidate sources scored:

- scPerturb, for harmonized public single-cell perturbation datasets.
- PerturBase, for a larger curated perturbation database with query and analysis modules.
- Tahoe-100M, for drug perturbation across many cancer cell lines.
- K562 Essential Perturb-seq Benchmark Dataset on the CZI Virtual Cells Platform, if a processed
  one-file benchmark is easier than the full Figshare set.
- pertpy's Replogle K562 loader, as a tooling route back to a known substrate.

Current result:

- 5 candidate sources scored.
- 0 go-now ingests.
- 3 scout-only sources: CZI K562 Essential, scPerturb, PerturBase.
- 2 no-go large-ingest routes: Tahoe-100M and the pertpy Replogle loader.
- 0 public app surfaces.

Decision:

- `do_not_ingest_new_large_dataset_before_submission`
- Next best action: `campaign_challenger_ledger`

Why this matters: not ingesting a huge corpus is an engineering and scientific decision, not a lack
of ambition. The shipped frontier already has cross-substrate replay, donor-condition replay, and
disease-context evidence. A rushed large-corpus ingest would add parser, license, and provenance
risk while giving judges less confidence than the existing replay packets.

Potential discovery:

- A third or fourth replay substrate that supports or contradicts campaign candidates.
- A drug-response contrast where a perturbation signature resembles a Prospect genetic perturbation,
  explicitly as hypothesis support only.

Deliverables:

- `./prospect perturbation-scout`
- `docs/PERTURBATION_ATLAS_SCOUT.md`
- `examples/data/perturbation_atlas_scout.json`

Status:

- Scout result is `evidence_attached`.
- Any small extracted table must be frozen and hashable before being used in a replay packet.
- No accepted-state mutation.

Gate:

- No public app surface unless the scout produces a real replay packet.
- Tests cover source count, decisions, recommendation, status, and forbidden strong language.
- `python tests/test_repo_hygiene.py`
- `./prospect final-check` for any committed generated artifact.

Go or no-go:

- Shipped as a scout packet.
- Do not ingest Tahoe-100M during the hackathon unless there is a small official subset with clear
  access and license fit. The source is scientifically exciting but too large for a rushed trust path.
- Do not use the pertpy Replogle loader as a new substrate. It is useful tooling, but not new
  frontier information.

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
  - donor-condition replay
  - cross-substrate discovery
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
2. Keep Workstream 2, Workstream 1, and Workstream 3 green: cross-substrate discovery,
   donor-condition replay, and disease-genetics overlay are now shipped frontier-advancement packets.
3. Keep Workstream 4 green: perturbation-atlas scout is shipped as a source-backed no-go for large
   ingestion before submission.
4. Run Workstream 5 only after the shipped advancement packets change the campaign ranking or assay
   framing.
5. Refresh demo, submit packet, judge packet, release manifest, and web data after any public artifact.
6. Deploy only after web or public-data changes, using the deployment command in `AGENTS.md`.

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

Do not start a new large data ingest before submission. Prospect has now shipped the defensible
frontier-advancement set: cross-substrate discovery, donor-condition replay, disease-genetics
overlay, and perturbation-atlas scout. The next highest-leverage technical move is a campaign
challenger ledger only if it can use those shipped packets to demote or promote rows without changing
accepted state. Otherwise, preserve the green floor, keep the demo tight, and let the project win on
the trust boundary plus the replay packets already shipped.
