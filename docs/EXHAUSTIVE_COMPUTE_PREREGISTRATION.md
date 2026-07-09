# Exhaustive compute pre-registration

ID: `exhaustive_prereg_7460abbb6f7337c1`

Frontier root: `root_a8b0dcdd4024e12f`. accepted=false. next=human_signature_required.

Ceiling: Computation over released data, not wet-lab or clinical truth.

No model is in the trust path. Anthropic budget: $0. A human key accepts no state in this run.

## Target Scale

- Literature: target thousands, stop only at configured max_records or exhausted Europe PMC cursors.
- Atlas: all 11,526 Marson genes, all Rest, Stim8hr, Stim48hr conditions.
- Leaderboard: all novel driver candidates absent from CollecTRI and standard T-cell annotations.

## Typed Status Ladder

- `evidence_attached`: comparable causal activation-driver claim and Marson on-target perturbation moves more than 10 transcripts at strongest effect
- `contradicted`: explicit causal activation-driver claim with comparable readout, but Marson on-target perturbation moves 10 or fewer transcripts at strongest effect
- `orthogonal_phenotype`: claim is about cytokine secretion, exhaustion, disease association, immunotherapy response, or another non-comparable readout
- `not_assayed`: gene is absent from the frozen Marson atlas or lacks comparable on-target coverage

## Literature Query Plan

- `CD4 T cell activation regulator`
- `CD4 T-cell activation regulator`
- `human CD4 T cell activation regulator`
- `primary CD4 T cell activation regulator`
- `CD4 T cell transcriptional regulator activation`
- `CD4 T cell TCR activation regulator`
- `TCR stimulated CD4 T cell regulator`
- `helper T cell activation regulator`
- `T helper cell activation regulator`
- `Th1 differentiation regulator CD4 T cell`
- `Th2 differentiation regulator CD4 T cell`
- `Th17 differentiation regulator CD4 T cell`
- `Tfh differentiation regulator CD4 T cell`
- `Treg activation regulator CD4 T cell`
- `CD4 T cell proliferation regulator`
- `CD4 T cell CRISPR screen regulator activation`
- `CRISPR CD4 T cell regulator activation`
- `Perturb-seq T cell activation regulator`
- `single cell CRISPR T cell activation regulator`
- `CD4 T cell immune synapse regulator`
- `CD4 T cell signaling regulator activation`
- `NFAT CD4 T cell activation regulator`
- `NF-kappaB CD4 T cell activation regulator`
- `AP-1 CD4 T cell activation regulator`
- `calcineurin CD4 T cell activation regulator`
- `costimulation CD4 T cell activation regulator`
- `CD28 CD4 T cell activation regulator`
- `IL2 CD4 T cell activation regulator`
- `checkpoint CD4 T cell activation regulator`
- `human T cell activation transcriptional regulator CD4`

## Comparability Rule

A contradiction requires an explicit causal activation-driver claim and a comparable activation, TCR stimulation, transcriptional program, proliferation, or differentiation readout. Cytokine secretion, exhaustion, disease association, immunotherapy response, and generic importance are `orthogonal_phenotype` unless the claim is explicitly narrowed to the Marson activation-transcriptome readout.

## Checkpoint Contract

- State: `output/exhaustive_compute/literature_state.json`
- Documents: `output/exhaustive_compute/literature_documents.jsonl`
- Claims: `output/exhaustive_compute/literature_claims.jsonl`
- Snapshot: `output/exhaustive_compute/literature_audit_snapshot.json`
- Log: `output/exhaustive_compute/run.log`
- Crash loss bound: at most the current Europe PMC page or current claim sentence.

## Public Artifact

- `/data/exhaustive_compute_preregistration.json`

## Reproduce

```bash
./prospect exhaustive-compute --phase preregister
```

## Source Inventory

- `frontier_signature`: `frontier/frontier.sig.json` sha256 `64bdb049ebfe0a6730f058919b69f556d19e9ef66adf6b3b7fcf663fe1f684b4`
- `marson_de_full`: `examples/data/marson_de_full.csv` sha256 `ef33a498f6dad50c2fb464cdbfcd558c0a17b5ac48f7efb07ac38068c20ede7b`
- `overnight_atlas`: `examples/data/overnight_genome_wide_atlas.json` sha256 `d3171af094de823131ecce0e10a957676f99522d7f689dcb60a97e7ac2251f53`
- `replogle_k562`: `examples/data/replogle_k562_de.csv` sha256 `a6a39225748fc6833f2204b67ed4993629cd3d6dfebd277c2cbbffb38615d204`
- `replogle_rpe1`: `examples/data/replogle_rpe1_de.csv` sha256 `fd4e03ea64616f45e3816e07e110badbfe98c313703f1e35372df1a163db3293`
- `collectri`: `examples/data/collectri_human.csv` sha256 `9e065f57f3da52b12b0b114da4dada6d8b39bb54dbfa405ae2c583d94cde622f`
- `cross_validation_sources`: `examples/data/cross_validation_sources.json` sha256 `69d5f5e89f3d10a84003f1c89c8d348425e3c0e09d49c7253594ccf72f61d8d0`
- `disease_overlay`: `examples/data/disease_genetics_overlay.json` sha256 `7955f52c8f019d6786f1d42f633957ce0e19dea8e9daa0319aac80ee51880179`

## Gate Commands

- `./prospect verify`
- `python benchmark/mutation_pack.py`
- `python tests/test_skill_parity.py`
- `python tests/test_marson.py`
- `python -m pytest tests/ -q`
- `cd web && npm run build`
