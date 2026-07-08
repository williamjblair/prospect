"""Print the final recording teleprompter."""
from __future__ import annotations

import argparse
import json

LIVE_URL = "https://prospect-sepia-six.vercel.app"
SIGNED_ROOT = "root_a8b0dcdd4024e12f"

BEATS = [
    {
        "time": "0:00",
        "title": "Refusal",
        "show": "Overview tab, opening A1BG claim card.",
        "say": (
            "This claim sounds plausible: CRISPRi of A1BG drives a broad activation program in "
            "stimulated CD4 T cells. The checker marks it unsupported because A1BG was not knocked "
            "down. A model can assert this in a second. Checking it is the scarce part."
        ),
    },
    {
        "time": "0:20",
        "title": "The Number",
        "show": "Overview headline and judge packet card.",
        "say": (
            "On a frozen Marson-screen sample, four frontier models made confident major-regulator "
            "claims, and 48% were contradicted by the measured data. On famous checkpoint and "
            "cytokine genes, the overclaim rate is 64%."
        ),
    },
    {
        "time": "0:40",
        "title": "Findings",
        "show": "Findings tab, scannable findings index, then Finding 01 and Finding 02.",
        "say": (
            "Prospect first recovers known biology. CD3E is quiet at Rest and broad after "
            "stimulation. Then it catches overclaims: PD-1, TIM-3, CTLA-4, and IL-2 are outputs "
            "here, not broad transcriptional drivers."
        ),
    },
    {
        "time": "1:05",
        "title": "The Moat",
        "show": "Finding 04 and the transfer replay packet.",
        "say": (
            "The same claim runs through Marson and Replogle checkers. MED19 moves 3,716 genes in "
            "K562. BCL10 moves 2. The transfer replay packet stays computationally_reproduced and "
            "changes no accepted state."
        ),
    },
    {
        "time": "1:30",
        "title": "The Loop",
        "show": "Agent tab, campaign pressure summary.",
        "say": (
            "Claude proposed fifteen transcription factors, then pressure-tested the campaign rows. "
            "Claude pressure became review work: eight probed rows, four more-aggressive calls "
            "converted to assay gates, and zero accepted-state mutations. Claude proposes, frozen "
            "code decides, and a human key accepts state."
        ),
    },
    {
        "time": "1:50",
        "title": "Close",
        "show": "Frontier receipt bridge, then Agent PGGT1B, pressure summary, and lab packet.",
        "say": (
            "The receipt bridge shows the boundary: external work can submit a receipt, but the "
            "result is accepted=false and next=human_signature_required. PGGT1B remains "
            "evidence_attached. The packet names missing wet-lab evidence, then gives assay-ready "
            "rows. Generation is cheap. Accepted state is scarce, replayable, and signed."
        ),
    },
]

DO_NOT_SAY = [
    "Do not claim wet-lab or clinical truth.",
    "Do not call PGGT1B an accepted regulator.",
    "Do not imply Claude can move accepted state.",
    "Do not call evidence_attached rows reproduced findings.",
]


def build_packet() -> dict[str, object]:
    return {
        "live_url": LIVE_URL,
        "signed_root": SIGNED_ROOT,
        "beats": BEATS,
        "do_not_say": DO_NOT_SAY,
        "preflight": [
            "./prospect final-check",
            "./prospect submit-smoke",
            "./prospect submit-pack",
            "./prospect demo-pack",
            "python examples/receipt_bridge_client.py --json",
        ],
    }


def _print_text(packet: dict[str, object]) -> None:
    print("Prospect demo teleprompter")
    print("")
    print(f"Live URL: {packet['live_url']}")
    print(f"Signed root: {packet['signed_root']}")
    print("")
    print("Preflight:")
    for command in packet["preflight"]:
        print(f"- {command}")
    print("")
    for beat in packet["beats"]:
        print(f"{beat['time']} {beat['title']}")
        print(f"Show: {beat['show']}")
        print(f"Say: {beat['say']}")
        print("")
    print("Do not say:")
    for line in packet["do_not_say"]:
        print(f"- {line}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect demo-pack")
    parser.add_argument("--json", action="store_true", help="emit the teleprompter packet as JSON")
    args = parser.parse_args(argv)

    packet = build_packet()
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        _print_text(packet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
