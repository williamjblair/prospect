# Prospect public release manifest

Live: [https://prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Repo: [https://github.com/williamjblair/prospect](https://github.com/williamjblair/prospect)

Signed root: `root_a8b0dcdd4024e12f`

## No model in the trust path

This manifest hashes the public data artifacts served by the app. It does not move accepted state. The signed frontier root is still gated by frozen replay and a human Ed25519 key.

## Hash scope

- Hash algorithm: `sha256`
- Public artifacts: 27
- Hashed artifacts: 26
- Manifest self hash: `excluded`

## Public artifact hashes

| path | bytes | sha256 |
|---|---:|---|
| `/data/frontier.json` | 5953696 | `1666efe5de1cd443594d8e270f942675eb30f82cf8296cdce17e66c98f78b893` |
| `/data/judge_packet.json` | 20814 | `66a8872c1078289b60fb9f1b390c6b424dadaf712266bcd22ed37ac7be2fe1bc` |
| `/data/finding_index.json` | 2711 | `3d5928ef636b49fe92f430e384f720fb28c08ba59b49e8b8c0e982c22565e01a` |
| `/data/receipt_bridge/receipt_contract.json` | 1803 | `eedc6262011cd5b4345e86c2f3ba362c8aff7fa1705fb1fa18b77fb8f6df731a` |
| `/data/receipt_bridge/receipt_manifest.json` | 1136 | `2e542c206b7f1ed8347e73b6fa372f7e74e1e6c7f00efda98b0508e82cad445a` |
| `/data/receipt_bridge/receipt_bundle.json` | 18735 | `8a931ffc668f2613643e8d2f9fcd69f4b8fddbc46f7a54ce4efebaf12e36b886` |
| `/data/pggt1b_deep_dive.json` | 10912 | `bb217db985541fdf7c35d9b397fc2dd756782eb778e70dc09fa5c4938bb79448` |
| `/data/pggt1b_matrix_slice.json` | 2445 | `3fa2af8c47f4edaebbb21dea8c4fb3e1ecefdb8126f672f2412f1a5dcb84a281` |
| `/data/agent_campaign.json` | 30164 | `9b1581e2d357f733ab1e6b9400922de292b2963a226b94330f09e156de9664e6` |
| `/data/agent_campaign_review.json` | 14555 | `ac5cb2bb8522a1ae38049db139c537b6f3d732487546dd251df613c734253223` |
| `/data/campaign_agent_probe.json` | 54286 | `0df468c2ab5599dd5499bb8ae94703877efb8268067761e4a3d423c143c97886` |
| `/data/campaign_probe_audit.json` | 1366 | `4d51685b7fe9d1588bf1c137cc6a8f3431d81707004c02d55e29bc74d850a10a` |
| `/data/campaign_triage.json` | 11777 | `39e4fce014fb0a84ce857ea3d3b2c878cee2bc451b9e41111513aec71885fd43` |
| `/data/campaign_gate_probe.json` | 87715 | `9eedf8ee67babe1c68e19f7168399d430a1f07f6c7f1872fb6b93d9c461f6dbb` |
| `/data/campaign_pressure_summary.json` | 13538 | `ac3faa262e69650ad352a22d8d97ce034920ad911a100c878d5f24a63de291cc` |
| `/data/campaign_challenger_ledger.json` | 17900 | `9a87620801edf120ba9e8907427dbd86c407d7626c84a28c75910921618d5bcf` |
| `/data/transfer_replay_packet.json` | 1480 | `3bb41d0e0eb3bb4da6579efee02899244a4b0c52bfbb22eb34562d224c825651` |
| `/data/substrate_replay_packet.json` | 3512 | `67b5a7ce085ae7d1777de640d03519208a4a7f2142338efc3851c795d6999895` |
| `/data/cross_substrate_discovery.json` | 29152 | `c7e2d0ce2e7427fde772bf189b58953990099be4deab03a9904ba2cd8513e3bf` |
| `/data/donor_condition_replay.json` | 25607 | `573f95532bdac014c3fd9a2cc1e13eb1e29014cef164234ad23b9ffbb0748ee6` |
| `/data/disease_genetics_overlay.json` | 51563 | `837511a9ad9d3edd1900eb4c9c9fc90e918b3e497032e0486e6d80a08facf957` |
| `/data/lab_packet.json` | 8656 | `3846f6b401e1f5325bac22ff3d25e3cacd4c88f588a3842511569af360a5840b` |
| `/data/assay_operations_bundle.json` | 14354 | `16de3c65459143096bc112ef372dd6dde215e778676173e1b08956241c871d85` |
| `/data/gladstone_pilot_design.json` | 10079 | `908967a92079c685f4f1ba038ba3b268ec61a91413ae6f95ff96d540cabd3ce0` |
| `/data/final_submission_audit.json` | 7752 | `f804cf906c81d8165ec3d2f26e36527a66f61bdf848177e103ee0dff2871fade` |
| `/data/rendered_qa_packet.json` | 2258 | `6e497255a87314ee129f388ef0275eb0dd16ba67605a6fb328b1233de5a6b8fa` |
| `/data/release_manifest.json` | n/a | `self_hash_excluded` |

Hashes prove deployed byte identity, not wet-lab or clinical truth.

Rebuild:

```bash
./prospect release-manifest
```
