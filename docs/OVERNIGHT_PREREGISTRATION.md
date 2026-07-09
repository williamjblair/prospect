# Overnight compute pre-registration

ID: `overnight_prereg_c2f80ef91baea329`

Frontier root: `root_a8b0dcdd4024e12f`. accepted=false. next=human_signature_required.

Ceiling: Computation over released data, not wet-lab or clinical truth.

No model is in the trust path. Anthropic budget: $0. The run is compute-only over frozen or newly frozen released data.

## Typed Status Ladder

- `evidence_attached`: on-target perturbation has a causal activation-program effect in the comparable substrate, but remains proposal-only
- `associative_only`: gene is present in an external signature or literature context, but perturbation does not support a causal driver role and no comparable driver claim is refuted
- `contradicted`: an explicit causal or driver claim with a comparable readout is refuted by on-target perturbation evidence
- `orthogonal_phenotype`: the comparator tests a different phenotype or readout, so it cannot support or contradict the activation-transcriptome claim
- `not_assayed`: gene is absent, lacks on-target perturbation, or the comparator does not cover it
- `refuted`: reserved for a stronger future packet where multiple comparable frozen sources overturn the same explicit claim

## Source Inventory

- `marson_cd4_activation`: `examples/data/marson_de_full.csv` sha256 `ef33a498f6dad50c2fb464cdbfcd558c0a17b5ac48f7efb07ac38068c20ede7b`
- `frontier_backbone`: `examples/data/atlas_backbone.json` sha256 `60ce305107d8d3d2f8b726c91c5c2afff970a4126d512f0abcff55ef6ae8122c`
- `replogle_k562`: `examples/data/replogle_k562_de.csv` sha256 `a6a39225748fc6833f2204b67ed4993629cd3d6dfebd277c2cbbffb38615d204`
- `replogle_rpe1`: `examples/data/replogle_rpe1_de.csv` sha256 `fd4e03ea64616f45e3816e07e110badbfe98c313703f1e35372df1a163db3293`
- `collectri`: `examples/data/collectri_human.csv` sha256 `9e065f57f3da52b12b0b114da4dada6d8b39bb54dbfa405ae2c583d94cde622f`
- `cross_validation_sources`: `examples/data/cross_validation_sources.json` sha256 `69d5f5e89f3d10a84003f1c89c8d348425e3c0e09d49c7253594ccf72f61d8d0`
- `cross_validation`: `examples/data/cross_validation.json` sha256 `f562de2b35a7fd3d012c53d17ac7da5c358cf28d89fdbfdf014a6b345f9b53e0`
- `disease_overlay`: `examples/data/disease_genetics_overlay.json` sha256 `7955f52c8f019d6786f1d42f633957ce0e19dea8e9daa0319aac80ee51880179`
- `frontier_signature`: `frontier/frontier.sig.json` sha256 `64bdb049ebfe0a6730f058919b69f556d19e9ef66adf6b3b7fcf663fe1f684b4`

## Phase 1 Rules

- Universe: all Marson genes grouped by `target_contrast_gene_name`.
- Strongest effect: maximum `n_total_de_genes` among on-target KD rows across Rest, Stim8hr, and Stim48hr.
- Driver threshold: strongest on-target effect greater than 10 DE genes.
- `associative_only`: strongest on-target effect from 0 to 10 DE genes when no comparable explicit driver claim is under test.
- `not_assayed`: no on-target KD row or missing comparator coverage.
- K562 is the genome-wide specificity comparator. RPE1 non-coverage is context only.

## Phase 2 Literature Rules

Europe PMC query plan:

- `human CD4 T cell activation regulator`
- `CD4 T cell transcriptional regulator activation`
- `T cell activation checkpoint regulator CD4`
- `CRISPR CD4 T cell regulator activation`
- `Perturb-seq T cell activation regulator`

Contradiction requires an explicit causal or driver claim, a comparable activation readout, and Marson on-target strongest effect at or below 10 DE genes. Non-comparable cytokine, disease, exhaustion, or immunotherapy-response claims are `orthogonal_phenotype`.

## Phase 3 Kill Rules

- `technical_confound`: fails if no on-target stimulated perturbation, failed knockdown, or off-target warning explains the effect
- `essentiality_or_proliferation_artifact`: fails if Rest reach, K562 transfer, RPE1 covered transfer, or DepMap dependency better explains the signal as general machinery
- `batch_or_donor_effect`: fails if a comparable frozen primary T-cell perturbation screen directly tests and does not support the driver claim
- `reverse_causality_or_passenger_marker`: fails if the frozen evidence supports downstream expression or association rather than causal perturbation
- `better_alternative_mechanism`: fails if STRING, pathway, disease, or chemistry evidence points to another node as the better causal explanation

A leaderboard entry remains proposal-only and accepted=false. A human key accepts no state overnight.
