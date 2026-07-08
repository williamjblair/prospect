# Prospect public release manifest

Live: [https://prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Repo: [https://github.com/williamjblair/prospect](https://github.com/williamjblair/prospect)

Signed root: `root_a8b0dcdd4024e12f`

## No model in the trust path

This manifest hashes the public data artifacts served by the app. It does not move accepted state. The signed frontier root is still gated by frozen replay and a human Ed25519 key.

## Hash scope

- Hash algorithm: `sha256`
- Public artifacts: 26
- Hashed artifacts: 25
- Manifest self hash: `excluded`

## Public artifact hashes

| path | bytes | sha256 |
|---|---:|---|
| `/data/frontier.json` | 5934061 | `f6683baed70e9cd8793e16fd9ebcb9956f5c613c4973c43b16ddbd16566e1516` |
| `/data/judge_packet.json` | 20205 | `bd81580b626c6ba70a3744a221fb7d3e39d6ac63249006990f2bfa6c209024f3` |
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
| `/data/transfer_replay_packet.json` | 1480 | `3bb41d0e0eb3bb4da6579efee02899244a4b0c52bfbb22eb34562d224c825651` |
| `/data/substrate_replay_packet.json` | 3512 | `67b5a7ce085ae7d1777de640d03519208a4a7f2142338efc3851c795d6999895` |
| `/data/cross_substrate_discovery.json` | 29152 | `c7e2d0ce2e7427fde772bf189b58953990099be4deab03a9904ba2cd8513e3bf` |
| `/data/donor_condition_replay.json` | 25607 | `573f95532bdac014c3fd9a2cc1e13eb1e29014cef164234ad23b9ffbb0748ee6` |
| `/data/disease_genetics_overlay.json` | 51563 | `837511a9ad9d3edd1900eb4c9c9fc90e918b3e497032e0486e6d80a08facf957` |
| `/data/lab_packet.json` | 8323 | `51f9791c309959831c1753d1f035dd465b7f9650cd74886facec395a2bbfa482` |
| `/data/assay_operations_bundle.json` | 14350 | `0d0f83dff0b992069c9c85c7a5d8e097b3ad6af9f63a05044730ce4b96bbd8eb` |
| `/data/gladstone_pilot_design.json` | 10075 | `804ede72ae41cd4dbbf10ca9245ce0834700768d3e2d9efdeeaaa480b7b64e95` |
| `/data/final_submission_audit.json` | 6999 | `255f5cb036c1619cd1575f0f54ec77bb3caab1a35292f562fc6e8c548076f796` |
| `/data/rendered_qa_packet.json` | 2209 | `fdd3ffc2a250acfc5b760c947f0b078103363808565baaa55186aa1ce475cf32` |
| `/data/release_manifest.json` | n/a | `self_hash_excluded` |

Hashes prove deployed byte identity, not wet-lab or clinical truth.

Rebuild:

```bash
./prospect release-manifest
```
