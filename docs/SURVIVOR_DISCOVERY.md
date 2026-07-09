# Survivor discovery

Status: `evidence_attached`. accepted=false. next=human_signature_required.

Ceiling: Computation over released data, not wet-lab or clinical truth.

The strict Prospect overnight gate reduced 2,734 novel causal-driver candidates to three proposal-only hypotheses: PGGT1B, CCDC22, and LETM2. They are not a settled module. They are three mechanistically distinct perturbation-backed hypotheses worth testing.

## Three Numbers

- Genome-wide genes typed: 11526
- Literature claims contradicted: 51 of 229
- Novel driver candidates scored: 2734
- Survivor hypotheses retained: 3

## Survivor Hypotheses

| rank | gene | axis | strongest condition | strongest DE | K562 DE | orthogonal datasets |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 | PGGT1B | prenylation and small-GTPase traffic | Stim8hr | 3014 | 1 | 6 |
| 2 | CCDC22 | CCC, COMMD, and retromer-associated endosomal traffic | Stim48hr | 619 | 13 | 6 |
| 3 | LETM2 | organelle ion homeostasis and late activation state | Stim48hr | 386 |  | 5 |

## Mechanistic Reads

### PGGT1B

PGGT1B may tune the stimulated CD4+ activation transcriptome through geranylgeranylation of small-GTPase traffic nodes that support immune-synapse and receptor-localization programs.

Why it matters: This connects a large Stim8hr perturbation effect to a concrete biochemical axis, with K562 specificity and Shifrut primary T-cell support.

Falsifiable experiment: CRISPRi knockdown of PGGT1B with at least two independent guides in Stim8hr; refutes if adequate PGGT1B knockdown does not shift the registered activation program in Stim8hr, or the same shift is explained by broad viability or housekeeping stress.

### CCDC22

CCDC22 may connect stimulated CD4+ activation state to CCC and COMMD retromer-associated trafficking, a route for receptor recycling and endosomal control rather than a canonical transcription factor route.

Why it matters: This is the cleanest genetic hook among the survivors, with immune-dysregulation context and a strong CCDC93, VPS35L, and COMMD protein-network neighborhood.

Falsifiable experiment: CRISPRi knockdown of CCDC22 with at least two independent guides in Stim48hr; refutes if adequate CCDC22 knockdown does not shift the registered activation program in Stim48hr, or the same shift is explained by broad viability or housekeeping stress.

### LETM2

LETM2 may affect the late stimulated CD4+ activation state through organelle ion-homeostasis biology, but its mechanistic bridge is weaker than PGGT1B or CCDC22 and must be tested directly.

Why it matters: It survives the full frozen compute bar with a low-Rest Marson signal, Shifrut support, DICE expression, and multiple-sclerosis pathway context, while staying visibly caveated.

Falsifiable experiment: CRISPRi knockdown of LETM2 with at least two independent guides in Stim48hr; refutes if adequate LETM2 knockdown does not shift the registered activation program in Stim48hr, or the same shift is explained by broad viability or housekeeping stress.

## What This Does Not Claim

- no wet-lab truth
- no accepted biological state
- no settled module
- no claim that bounded literature silence proves novelty

## Public Artifact

- `/data/survivor_discovery.json`

## Reproduce

```bash
./prospect survivor-discovery
```
