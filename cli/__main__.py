"""One entrypoint for the whole loop. `python -m cli <command>` (or the ./prospect wrapper).

  prospect build            rebuild the frontier from frozen data
  prospect verify           re-derive every object (EXACT-lane, 0 drift)
  prospect sign             the human ceremony: accept the frontier root
  prospect check <claims>   grade typed claims against a dataset  (--dataset --data --out)
  prospect propose          Claude proposes → the frozen verifier decides  (--n --model --sign)
  prospect agent            autonomous Claude agent: search → verify → converge  (--sign)
  prospect campaign         build the proposal-only agent campaign leaderboard
  prospect findings-index   build the scannable finding index for the demo
  prospect judge-pack       build the judge packet manifest and handoff
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
    elif cmd == "findings-index":
        from frontier.finding_index import main as finding_index_main; finding_index_main()
    elif cmd == "judge-pack":
        from frontier.judge_packet import main as judge_packet_main; judge_packet_main()
    elif cmd == "receipt":
        from receipt.emit import main as receipt_main; receipt_main(rest)
    elif cmd == "mcp":
        from receipt.mcp_server import main as mcp_main; mcp_main()
    else:
        print(__doc__)
        sys.exit(0 if cmd in ("help", "-h", "--help") else 2)

if __name__ == "__main__":
    main()
