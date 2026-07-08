# Prospect Demo Teleprompter

Use this as the spoken script while recording the two-minute Built with Claude: Life Sciences demo.
For a terminal copy, run:

```bash
./prospect demo-pack
```

Live URL: https://prospect-sepia-six.vercel.app

Signed root: `root_a8b0dcdd4024e12f`

## Preflight

```bash
./prospect final-check
./prospect submit-smoke
./prospect submit-pack
./prospect demo-pack
./prospect judge-handout
./prospect release-manifest
./prospect rendered-qa
./prospect browser-qa --target both # optional, after local web starts on 8124
python examples/receipt_bridge_client.py --json
```

## Script

### 0:00, Refusal

Show: Overview tab, opening A1BG claim card.

Say: This claim sounds plausible: CRISPRi of A1BG drives a broad activation program in stimulated
CD4 T cells. The checker marks it unsupported because A1BG was not knocked down. A model can assert
this in a second. Checking it is the scarce part.

### 0:20, The Number

Show: Overview headline and judge packet card.

Say: On a frozen Marson-screen sample, four frontier models made confident major-regulator claims,
and 48% were contradicted by the measured data. On famous checkpoint and cytokine genes, the
overclaim rate is 64%.

### 0:40, Findings

Show: Findings tab, scannable findings index, then Finding 01 and Finding 02.

Say: Prospect first recovers known biology. CD3E is quiet at Rest and broad after stimulation. Then
it catches overclaims: PD-1, TIM-3, CTLA-4, and IL-2 are outputs here, not broad transcriptional
drivers.

### 1:05, The Moat

Show: Finding 04, the transfer replay packet, and the substrate replay packet.

Say: The same claim runs through Marson and Replogle checkers. MED19 moves 3,716 genes in K562.
BCL10 moves 2. The transfer replay packet stays `computationally_reproduced` and changes no accepted
state.

### 1:30, The Loop

Show: Agent tab, campaign pressure summary.

Say: Claude proposed fifteen transcription factors, then pressure-tested the campaign rows. Claude
pressure became review work: eight probed rows, four more-aggressive calls converted to assay gates,
and zero accepted-state mutations. Claude proposes, frozen code decides, and a human key accepts
state.

### 1:50, Close

Show: Frontier receipt bridge, then Agent PGGT1B, pressure summary, lab packet, assay operations bundle, and pilot design.

Say: The receipt bridge shows the boundary: external work can submit a receipt, but the result is
`accepted=false` and `next=human_signature_required`. PGGT1B remains `evidence_attached`. The packet
names missing wet-lab evidence, then gives assay-ready rows. The operations bundle says what would
promote, weaken, or reject each row before any status change, and the pilot design turns that into
90 proposal-only culture arms. Generation is cheap. Accepted state is scarce, replayable, and signed.

## Do Not Say

- Do not claim wet-lab or clinical truth.
- Do not call PGGT1B an accepted regulator.
- Do not imply Claude can move accepted state.
- Do not call `evidence_attached` rows reproduced findings.
