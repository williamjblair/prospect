"""Render a list of Verdicts into one self-contained HTML page - the deliverable
a scientist keeps. No external assets; opens offline."""
from __future__ import annotations
import html, json
from typing import List
from engine.schema import Verdict

_STATUS = {
    "supported":           ("Supported",           "#1a7f37", "#e6f4ea", "✓"),
    "refuted":             ("Refuted",             "#b3261e", "#fce8e6", "✗"),
    "unsupported":         ("Unsupported",         "#b3261e", "#fce8e6", "✗"),
    "needs_qualification": ("Needs qualification",  "#8a6d00", "#fef7e0", "⚠"),
    "asserted":            ("Interpretive",        "#5f6368", "#f1f3f4", "○"),
}

def _card(v: Verdict) -> str:
    label, fg, bg, glyph = _STATUS[v.status]
    ev_rows = ""
    for cond, e in (v.evidence or {}).items():
        cells = " · ".join(f"{k}: <b>{html.escape(str(val))}</b>" for k, val in e.items() if k != "condition")
        ev_rows += f'<div class="ev"><span class="cond">{html.escape(str(cond))}</span> {cells}</div>'
    mism = f'<span class="mism">{html.escape(v.mismatch_class)}</span>' if v.mismatch_class else ""
    return f"""
    <div class="card" style="border-left:4px solid {fg}">
      <div class="pill" style="color:{fg};background:{bg}">{glyph} {label}{mism}</div>
      <div class="claim">{html.escape(v.claim.text)}</div>
      <div class="reason">{html.escape(v.reason)}</div>
      {'<div class="evbox">'+ev_rows+'</div>' if ev_rows else ''}
    </div>"""

def render_html(verdicts: List[Verdict], dataset: str) -> str:
    n = len(verdicts)
    supported = sum(1 for v in verdicts if v.status == "supported")
    flagged = sum(1 for v in verdicts if v.status in ("refuted", "unsupported"))
    cards = "\n".join(_card(v) for v in verdicts)
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Second Opinion - claim check</title>
<style>
 body{{font:16px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;color:#1f2328;background:#fafbfc;margin:0}}
 .wrap{{max-width:760px;margin:0 auto;padding:32px 20px 64px}}
 h1{{font-size:22px;margin:0 0 4px}} .sub{{color:#656d76;margin:0 0 24px;font-size:14px}}
 .headline{{display:flex;gap:20px;margin:0 0 24px;padding:16px 18px;background:#fff;border:1px solid #d0d7de;border-radius:10px}}
 .headline b{{font-size:24px;display:block}} .headline span{{color:#656d76;font-size:13px}}
 .card{{background:#fff;border:1px solid #d0d7de;border-radius:10px;padding:16px 18px;margin:0 0 12px}}
 .pill{{display:inline-block;font-size:12px;font-weight:600;padding:3px 10px;border-radius:999px;margin-bottom:8px}}
 .mism{{opacity:.6;font-weight:400;margin-left:6px}}
 .claim{{font-size:16px;font-weight:600;margin:2px 0 6px}}
 .reason{{color:#424a53;font-size:14px}}
 .evbox{{margin-top:10px;padding-top:10px;border-top:1px solid #eaeef2}}
 .ev{{font-size:12.5px;color:#57606a;margin:2px 0}} .cond{{display:inline-block;min-width:64px;color:#1f2328;font-weight:600}}
 .foot{{color:#8b949e;font-size:12px;margin-top:28px}}
</style></head><body><div class="wrap">
 <h1>Second Opinion</h1>
 <p class="sub">Independent check of AI-generated claims against released ground-truth data · <b>{html.escape(dataset)}</b></p>
 <div class="headline">
   <div><b>{supported}/{n}</b><span>supported by the data</span></div>
   <div><b style="color:#b3261e">{flagged}</b><span>should not be reported as-is</span></div>
 </div>
 {cards}
 <p class="foot">Verdicts computed by frozen code against a frozen released table. No model in the trust path.
 "Supported" means the data reproduces the quantitative claim - never that the biology is true.</p>
</div></body></html>"""
