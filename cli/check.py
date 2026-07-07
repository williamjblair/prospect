"""prospect check - run typed claims through a dataset checker, print a
terminal summary, and write the one-page HTML report.

  python -m cli.check examples/claims_demo.json --dataset marson \
      --data examples/data/marson_de_demo_slice.csv --out report.html
"""
from __future__ import annotations
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.schema import Claim
from engine.registry import get_checker
from report.render import render_html

_COLOR = {"supported": "\033[32m", "refuted": "\033[31m", "unsupported": "\033[31m",
          "needs_qualification": "\033[33m", "asserted": "\033[90m"}
_R = "\033[0m"

def main(argv=None):
    ap = argparse.ArgumentParser(prog="prospect check")
    ap.add_argument("claims", help="JSON file: list of claim objects")
    ap.add_argument("--dataset", default="marson")
    ap.add_argument("--data", required=True, help="path to the released ground-truth table")
    ap.add_argument("--out", default="report.html")
    a = ap.parse_args(argv)

    claims = [Claim(**c) for c in json.load(open(a.claims))]
    checker = get_checker(a.dataset, a.data)
    verdicts = [checker.check(c) for c in claims]

    for v in verdicts:
        c = _COLOR.get(v.status, "")
        print(f"{c}{v.status.upper():20s}{_R} {v.claim.text}")
        print(f"                     └ {v.reason}")
    n = len(verdicts); ok = sum(v.status == "supported" for v in verdicts)
    flag = sum(v.status in ("refuted", "unsupported") for v in verdicts)
    print(f"\n{ok}/{n} supported · {flag} should not be reported as-is")

    open(a.out, "w").write(render_html(verdicts, a.dataset))
    print(f"report → {a.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
