"""One entrypoint for the whole loop. `python -m cli <command>` (or the ./prospect wrapper).

  prospect build            rebuild the frontier from frozen data
  prospect verify           re-derive every object (EXACT-lane, 0 drift)
  prospect sign             the human ceremony: accept the frontier root
  prospect check <claims>   grade typed claims against a dataset  (--dataset --data --out)
  prospect propose          Claude proposes, the frozen verifier decides  (--n --model --sign)
  prospect agent            autonomous Claude agent: search, verify, converge  (--sign)
  prospect campaign         build the proposal-only agent campaign leaderboard
  prospect discovery-campaign build the whole-frontier novelty campaign packet
  prospect cross-validation build the independent cross-validation packet
  prospect defended-discovery-preregister build the defended discovery pre-registration packet
  prospect pggt1b-defended-evidence build the rank-1 PGGT1B defended-evidence packet
  prospect flagship-module build the flagship mechanistic module packet
  prospect overclaim-counter build the overclaim refusal counter packet
  prospect disease-overlay  attach external disease-genetics context (Open Targets)
  prospect pggt1b           build the PGGT1B evidence packet
  prospect lab-pack         build the wet-lab assay packet
  prospect writeback        build the lab writeback receipt shape
  prospect findings-index   build the scannable finding index
  prospect judge-handout    build the one-page judge handout
  prospect submit-pack      print the copy-safe submission packet
  prospect receipt          emit portable receipts (activity to signed replayable state)
  prospect mcp              expose the receipt bridge over MCP stdio

The loop: propose (Claude), check/verify (frozen code), sign (human key). No model in the trust path.
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
    elif cmd == "discovery-campaign":
        from frontier.discovery_campaign import main as discovery_main; discovery_main()
    elif cmd == "cross-validation":
        from frontier.cross_validation import main as cross_validation_main; cross_validation_main()
    elif cmd == "defended-discovery-preregister":
        from frontier.defended_discovery_preregistration import main as preregister_main; preregister_main()
    elif cmd == "pggt1b-defended-evidence":
        from frontier.pggt1b_defended_evidence import main as pggt1b_defended_main; sys.exit(pggt1b_defended_main(rest))
    elif cmd == "flagship-module":
        from frontier.flagship_module import main as flagship_module_main; flagship_module_main()
    elif cmd == "overclaim-counter":
        from frontier.overclaim_counter import main as overclaim_counter_main; overclaim_counter_main()
    elif cmd == "disease-overlay":
        from frontier.disease_genetics_overlay import main as disease_main; sys.exit(disease_main(rest))
    elif cmd == "pggt1b":
        from frontier.pggt1b_deep_dive import main as pggt1b_main; pggt1b_main()
    elif cmd == "lab-pack":
        from frontier.lab_packet import main as lab_packet_main; lab_packet_main()
    elif cmd == "writeback":
        from receipt.writeback import main as writeback_main; writeback_main(rest)
    elif cmd == "findings-index":
        from frontier.finding_index import main as finding_index_main; finding_index_main()
    elif cmd == "judge-handout":
        from cli.judge_handout import main as judge_handout_main; sys.exit(judge_handout_main(rest))
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
