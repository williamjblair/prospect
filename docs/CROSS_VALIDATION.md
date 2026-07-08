# Phase 2 cross-validation

Status: `evidence_attached`. Trust boundary: proposal only. No external evidence moves accepted state.

Honest ceiling: computation over released data, not wet-lab or clinical truth.

Sources: Shifrut 2018 primary human T-cell SLICE screens, Schmidt 2022 primary human CD4+ CRISPRa cytokine screen, STRING protein network, DICE immune-cell expression, and the existing Open Targets overlay.

Schmidt comparability: `orthogonal_phenotype`. The Schmidt screen calls regulators of stimulation-responsive cytokine production and protein accumulation. The Marson replay measures activation-transcriptome breadth by stimulated differential-expression counts. A Schmidt non-hit is retained as evidence, but it is not a comparable contradiction of the Marson activation-transcriptome hypothesis.

## Counts

- Candidates: 18
- With at least one independent screen hit: 4
- With explicit Schmidt 2022 non-hit rows: 18
- Retyped as Schmidt orthogonal phenotype: 18
- With comparable external contradictions: 0
- With STRING interaction context: 17
- With DICE activated CD4 expression: 18

## Candidate ladder

| rank | gene | tier | screen support | Schmidt status | contradiction | DICE activated CD4 mean TPM | STRING partners | disease context |
|---:|---|---|---|---|---|---:|---|---|
| 1 | PGGT1B | screen_hit_plus_context | shifrut_2018_1107 | schmidt_2022_2427 |  | 16.101 | FNTA, HEYL, RABGGTA, CCDC112 | immune_context |
| 2 | RCC1L | context_only |  | schmidt_2022_2427 |  | 10.784 | RPUSD4, TRUB2, NGRN, NEK6 | immune_context |
| 3 | MCAT | context_only |  | schmidt_2022_2427 |  | 23.3 | OXSM, NDUFAB1, FASN, ACACA | immune_context |
| 4 | RWDD2B | context_only |  | schmidt_2022_2427 |  | 7.941 |  | immune_context |
| 5 | CCDC22 | screen_hit_plus_context | shifrut_2018_1107 | schmidt_2022_2427 |  | 30.218 | CCDC93, VPS35L, COMMD1, COMMD8 | genetic_context |
| 6 | GAS2L1 | context_only |  | schmidt_2022_2427 |  | 0.031 | RASL10A, AP1B1, MAPRE3, MAPRE1 | immune_context |
| 7 | SNAP29 | context_only |  | schmidt_2022_2427 |  | 12.202 | STX17, ATG14, VAMP7, VAMP8 | immune_context |
| 8 | CYB5RL | context_only |  | schmidt_2022_2427 |  | 2.774 | CYB5B, CYB5A, DHODH, DPYD | immune_context |
| 9 | LETM2 | screen_hit_plus_context | shifrut_2018_1109 | schmidt_2022_2427 |  | 2.731 | GOT1L1, NSD3, RAB11FIP1, DDHD2 | immune_context |
| 10 | DAPK2 | context_only |  | schmidt_2022_2427 |  | 0.33 | CALM3, BECN1, CALM2, MAPK3 | immune_context |
| 11 | SCO2 | context_only |  | schmidt_2022_2427 |  | 0.0 | MT-CO2, COX17, COX15, SURF1 | genetic_context |
| 12 | CCDC136 | context_only |  | schmidt_2022_2427 |  | 1.419 | MEGF10, TMEM8B, GCC2, MEGF6 | immune_context |
| 13 | MITD1 | context_only |  | schmidt_2022_2427 |  | 63.126 | CHMP1A, CHMP2A, VPS4A, IST1 | immune_context |
| 14 | GZMB | context_only |  | schmidt_2022_2427 |  | 7.422 | PRF1, GNLY, CASP3, DFFA | genetic_context |
| 15 | FANCL | context_only |  | schmidt_2022_2427 |  | 3.398 | HES1, FAAP100, FANCG, FANCB | immune_context |
| 16 | TNNC1 | screen_hit_plus_context | shifrut_2018_1107 | schmidt_2022_2427 |  | 4.171 | TNNT2, TNNI2, TNNI3, TNNI1 | immune_context |
| 17 | BCKDHA | context_only |  | schmidt_2022_2427 |  | 0.121 | BCKDHB, PDHB, DBT, DLD | immune_context |
| 18 | ZC3H12A | context_only |  | schmidt_2022_2427 |  | 262.315 | TANK, REG1B, REG1A, NFKBIZ | immune_context |

Rebuild:

```bash
./prospect cross-validation
```
