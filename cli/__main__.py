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
  prospect defended-discovery-endgame-preregister build the stricter endgame pre-registration packet
  prospect pggt1b-defended-evidence build the rank-1 PGGT1B defended-evidence packet
  prospect pggt1b-endgame-decision decide rank-1 PGGT1B under the endgame pre-registration
  prospect defended-candidate-decisions build the defended-discovery decision ledger
  prospect rcc1l-defended-evidence build the rank-2 RCC1L defended-evidence packet
  prospect mcat-defended-evidence build the rank-3 MCAT defended-evidence packet
  prospect rwdd2b-defended-evidence build the rank-4 RWDD2B defended-evidence packet
  prospect ccdc22-defended-evidence build the rank-5 CCDC22 defended-evidence packet
  prospect flagship-module build the flagship mechanistic module packet
  prospect overclaim-counter build the overclaim refusal counter packet
  prospect disease-overlay  attach external disease-genetics context (Open Targets)
  prospect pggt1b           build the PGGT1B evidence packet
  prospect lab-pack         build the wet-lab assay packet
  prospect writeback        build the lab writeback receipt shape
  prospect claude-science   build the real Claude Science acceptance-layer packet
  prospect findings-index   build the scannable finding index
  prospect judge-handout    build the one-page judge handout
  prospect submit-pack      print the copy-safe submission packet
  prospect receipt          emit portable receipts (activity to signed replayable state)
  prospect mcp              expose the receipt bridge over MCP stdio
  prospect serve-acceptance expose paste, HTTP, and MCP-style acceptance endpoints

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
    elif cmd == "defended-discovery-endgame-preregister":
        from frontier.defended_discovery_endgame_preregistration import main as endgame_preregister_main; endgame_preregister_main()
    elif cmd == "pggt1b-defended-evidence":
        from frontier.pggt1b_defended_evidence import main as pggt1b_defended_main; sys.exit(pggt1b_defended_main(rest))
    elif cmd == "pggt1b-endgame-decision":
        from frontier.rank1_pggt1b_endgame_decision import main as pggt1b_endgame_main; pggt1b_endgame_main()
    elif cmd == "defended-candidate-decisions":
        from frontier.defended_candidate_decisions import main as decisions_main; decisions_main()
    elif cmd == "rcc1l-defended-evidence":
        from frontier.rcc1l_defended_evidence import main as rcc1l_defended_main; rcc1l_defended_main()
    elif cmd == "mcat-defended-evidence":
        from frontier.mcat_defended_evidence import main as mcat_defended_main; mcat_defended_main()
    elif cmd == "rwdd2b-defended-evidence":
        from frontier.rwdd2b_defended_evidence import main as rwdd2b_defended_main; rwdd2b_defended_main()
    elif cmd == "ccdc22-defended-evidence":
        from frontier.ccdc22_defended_evidence import main as ccdc22_defended_main; ccdc22_defended_main()
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
    elif cmd == "claude-science":
        from receipt.causal_bridge import write_claude_science_packet
        packet = write_claude_science_packet()
        counts = packet["prospect"]["typed_status_counts"]
        print(
            "wrote examples/data/claude_science_acceptance_demo.json "
            f"({counts['genes']} genes, {counts['evidence_attached']} evidence_attached, "
            f"{counts['associative_only']} associative_only, {counts['contradicted']} contradicted, "
            f"{counts['not_assayed']} not_assayed)"
        )
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
    elif cmd == "serve-acceptance":
        from services.prospect_acceptance_service import main as service_main; sys.exit(service_main(rest))
    else:
        print(__doc__)
        sys.exit(0 if cmd in ("help", "-h", "--help") else 2)

if __name__ == "__main__":
    main()
