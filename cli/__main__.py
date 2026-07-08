"""One entrypoint for the whole loop. `python -m cli <command>` (or the ./prospect wrapper).

  prospect build            rebuild the frontier from frozen data
  prospect verify           re-derive every object (EXACT-lane, 0 drift)
  prospect sign             the human ceremony: accept the frontier root
  prospect check <claims>   grade typed claims against a dataset  (--dataset --data --out)
  prospect propose          Claude proposes → the frozen verifier decides  (--n --model --sign)
  prospect agent            autonomous Claude agent: search → verify → converge  (--sign)
  prospect campaign         build the proposal-only agent campaign leaderboard
  prospect campaign-review  build the campaign review appendix
  prospect campaign-probe   run Claude probes against campaign rows
  prospect campaign-triage  build deterministic triage from probe disagreements
  prospect campaign-gate-probe run Claude probes against disagreement assay gates
  prospect campaign-pressure build the campaign pressure summary packet
  prospect transfer-replay  build a compact transfer replay packet
  prospect substrate-replay build the protocol-generalization substrate replay packet
  prospect pggt1b           build the PGGT1B evidence packet
  prospect lab-pack         build the wet-lab assay packet
  prospect findings-index   build the scannable finding index for the demo
  prospect demo-pack        print the final recording teleprompter
  prospect judge-pack       build the judge packet manifest and handoff
  prospect final-check      run the local submission gate
  prospect submit-smoke     run production submission smoke checks
  prospect submit-pack      print the copy-safe submission packet
  prospect receipt          emit portable receipts (activity → signed replayable state)
  prospect mcp              expose the receipt bridge over MCP stdio

The loop: propose (Claude) → check/verify (frozen code) → sign (human key). No model in the trust path.
A receipt is the portable proposal that crosses the boundary from activity into state.
"""
import sys

def main():
    argv = sys.argv[1:]
    cmd = argv[0] if argv else "help"
    rest = argv[1:]

    if cmd == "build":
        from frontier.build import build; build()
    elif cmd == "verify":
        from frontier.verify import verify; ok, _ = verify(); sys.exit(0 if ok else 1)
    elif cmd == "sign":
        from frontier.sign import main as sign_main; sign_main()   # reads sys.argv (--yes)
    elif cmd == "check":
        from cli.check import main as check_main; sys.exit(check_main(rest))
    elif cmd == "propose":
        from loop.propose import main as propose_main; propose_main(rest)
    elif cmd == "agent":
        from loop.agent import main as agent_main; agent_main(rest)
    elif cmd == "campaign":
        from frontier.agent_campaign import main as campaign_main; campaign_main()
    elif cmd == "campaign-review":
        from frontier.campaign_review import main as campaign_review_main; campaign_review_main()
    elif cmd == "campaign-probe":
        from loop.campaign_probe import main as campaign_probe_main; campaign_probe_main(rest)
    elif cmd == "campaign-triage":
        from frontier.campaign_triage import main as campaign_triage_main; campaign_triage_main()
    elif cmd == "campaign-gate-probe":
        from loop.campaign_gate_probe import main as campaign_gate_probe_main; campaign_gate_probe_main(rest)
    elif cmd == "campaign-pressure":
        from frontier.campaign_pressure_summary import main as campaign_pressure_main; campaign_pressure_main()
    elif cmd == "transfer-replay":
        from frontier.transfer_replay import main as transfer_replay_main; transfer_replay_main()
    elif cmd == "substrate-replay":
        from frontier.substrate_replay import main as substrate_replay_main; substrate_replay_main()
    elif cmd == "pggt1b":
        from frontier.pggt1b_deep_dive import main as pggt1b_main; pggt1b_main()
    elif cmd == "lab-pack":
        from frontier.lab_packet import main as lab_packet_main; lab_packet_main()
    elif cmd == "findings-index":
        from frontier.finding_index import main as finding_index_main; finding_index_main()
    elif cmd == "demo-pack":
        from cli.demo_pack import main as demo_pack_main; sys.exit(demo_pack_main(rest))
    elif cmd == "judge-pack":
        from frontier.judge_packet import main as judge_packet_main; judge_packet_main()
    elif cmd == "final-check":
        from cli.final_check import main as final_check_main; sys.exit(final_check_main(rest))
    elif cmd == "submit-smoke":
        from cli.submit_smoke import main as submit_smoke_main; sys.exit(submit_smoke_main(rest))
    elif cmd == "submit-pack":
        from cli.submit_pack import main as submit_pack_main; sys.exit(submit_pack_main(rest))
    elif cmd == "receipt":
        from receipt.emit import main as receipt_main; receipt_main(rest)
    elif cmd == "mcp":
        from receipt.mcp_server import main as mcp_main; mcp_main()
    else:
        print(__doc__)
        sys.exit(0 if cmd in ("help", "-h", "--help") else 2)

if __name__ == "__main__":
    main()
