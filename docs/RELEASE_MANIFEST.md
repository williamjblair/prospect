# Prospect public release manifest

Live: [https://prospect-sepia-six.vercel.app](https://prospect-sepia-six.vercel.app)

Repo: [https://github.com/williamjblair/prospect](https://github.com/williamjblair/prospect)

Signed root: `root_a8b0dcdd4024e12f`

## No model in the trust path

This manifest hashes the public data artifacts served by the app. It does not move accepted state. The signed frontier root is still gated by frozen replay and a human Ed25519 key.

## Hash scope

- Hash algorithm: `sha256`
- Public artifacts: 23
- Hashed artifacts: 22
- Manifest self hash: `excluded`

## Public artifact hashes

| path | bytes | sha256 |
|---|---:|---|
| `/data/frontier.json` | 5700949 | `bd4a768c45dcb9cfc9bbfd6b4cad6fc15fcf1949ab356df9dcf52d501caec26f` |
| `/data/judge_packet.json` | 17625 | `36530260119607a04c2d9384d3959de6105fabc36856c4de4879a16aaa71a7c0` |
| `/data/finding_index.json` | 2711 | `3d5928ef636b49fe92f430e384f720fb28c08ba59b49e8b8c0e982c22565e01a` |
| `/data/receipt_bridge/receipt_contract.json` | 1803 | `eedc6262011cd5b4345e86c2f3ba362c8aff7fa1705fb1fa18b77fb8f6df731a` |
| `/data/receipt_bridge/receipt_manifest.json` | 1136 | `2e542c206b7f1ed8347e73b6fa372f7e74e1e6c7f00efda98b0508e82cad445a` |
| `/data/receipt_bridge/receipt_bundle.json` | 18735 | `8a931ffc668f2613643e8d2f9fcd69f4b8fddbc46f7a54ce4efebaf12e36b886` |
| `/data/pggt1b_deep_dive.json` | 10912 | `bb217db985541fdf7c35d9b397fc2dd756782eb778e70dc09fa5c4938bb79448` |
| `/data/pggt1b_matrix_slice.json` | 2445 | `3fa2af8c47f4edaebbb21dea8c4fb3e1ecefdb8126f672f2412f1a5dcb84a281` |
| `/data/agent_campaign.json` | 30164 | `9b1581e2d357f733ab1e6b9400922de292b2963a226b94330f09e156de9664e6` |
| `/data/agent_campaign_review.json` | 14555 | `ac5cb2bb8522a1ae38049db139c537b6f3d732487546dd251df613c734253223` |
| `/data/campaign_agent_probe.json` | 19306 | `bbcb8837d47fc921e7c824dab2fc7ea9e0b4b8faa47ccdf445e0024f4cb6cc64` |
| `/data/campaign_probe_audit.json` | 1145 | `bee3662b2ba80832e4dac7199820477b8494af2e4f4818a8b61471be5d166fac` |
| `/data/campaign_triage.json` | 4268 | `677446a7344ee41e96638569bfc0cccceeafcee1e451acd9e78df55efa462121` |
| `/data/campaign_gate_probe.json` | 15377 | `d87a941d138db73e7bbb833567a8f041854848a8ebd512f455d44ec994f1c62b` |
| `/data/campaign_pressure_summary.json` | 5788 | `70a1564915ec71d9b3646f23443fb66a3811b4dab8a89e523c0bea5c32fddac4` |
| `/data/transfer_replay_packet.json` | 1480 | `3bb41d0e0eb3bb4da6579efee02899244a4b0c52bfbb22eb34562d224c825651` |
| `/data/substrate_replay_packet.json` | 3512 | `67b5a7ce085ae7d1777de640d03519208a4a7f2142338efc3851c795d6999895` |
| `/data/lab_packet.json` | 8323 | `51f9791c309959831c1753d1f035dd465b7f9650cd74886facec395a2bbfa482` |
| `/data/assay_operations_bundle.json` | 14350 | `0d0f83dff0b992069c9c85c7a5d8e097b3ad6af9f63a05044730ce4b96bbd8eb` |
| `/data/gladstone_pilot_design.json` | 10075 | `804ede72ae41cd4dbbf10ca9245ce0834700768d3e2d9efdeeaaa480b7b64e95` |
| `/data/final_submission_audit.json` | 5676 | `04fae2fb716a5dda13f526e98c89b11ed828047ac3f92e987ee38983dc719708` |
| `/data/rendered_qa_packet.json` | 1876 | `b8eadc8ccc8973aab65bddc33e2ffd9f63b2ff7a77d77da1d08c45c466e4d3c9` |
| `/data/release_manifest.json` | n/a | `self_hash_excluded` |

Hashes prove deployed byte identity, not wet-lab or clinical truth.

Rebuild:

```bash
./prospect release-manifest
```
