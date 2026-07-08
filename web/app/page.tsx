"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  LayoutGrid, Rows3, Share2, Waypoints, Telescope, Search, ShieldCheck, ExternalLink, Bot,
} from "lucide-react";
import { useTheme } from "next-themes";
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent,
  SidebarHeader, SidebarInset, SidebarMenu, SidebarMenuButton, SidebarMenuItem,
  SidebarProvider, SidebarTrigger,
} from "@/components/ui/sidebar";
import { ThemeToggle } from "@/components/theme-toggle";
import { GraphView } from "@/components/graph-view";

type Cond = { s: string; de: number; dn: number; es: number };
type Node = { g: string; cls: string; st: string; od: number; id: number; C: Record<string, Cond> };
type Edge = { t?: string; s?: string; d: string; e: number };
type Contra = { gene: string; claimant: string; claim: string; verdict: string; reason: string };
type Finding = { kind: string; claim: string; status: string; n_genes: number; genes: string[]; evidence: any; cid: string };
type Cite = { pmid: string; doi: string; first_author: string; journal: string; year: number; canonical_role: string };
type FindingIndex = {
  status: string;
  source: string;
  items: {
    rank: number; kind: string; title: string; status: string; challenge_status: string; n_genes: number;
    cid: string; question: string; readout: string; takeaway: string; demo_genes: string[];
  }[];
};
type PGGT1BDeepDive = {
  gene: string;
  status: string;
  claim_scope: string;
  claim: string;
  prospect_read: string;
  assay_readout: string;
  facts: {
    rest_de: number; rest_kd: string; stim8hr_de: number; stim8hr_kd: string;
    stim48hr_de: number; stim48hr_kd: string; k562_de: number | null;
    rpe1_de: number | null; collectri_targets: number; graph_edges_sliced: number;
  };
  validation_plan?: {
    status: string; trust_boundary: string; sample: string; intervention: string; primary_readout: string;
    mechanism_readouts: string[]; negative_controls: string[]; positive_controls: string[];
    expected_pattern: string; stop_rules: string[];
  };
  literature_context: { journal: string; year: number; doi: string; url: string; why_it_matters: string }[];
  caveats: string[];
};
type AgentCampaign = {
  campaign_id: string;
  title: string;
  status: string;
  trust_boundary: string;
  acceptance: boolean;
  method: { min_stim_de: number; max_rest_de: number; filters: string[] };
  candidates: {
    rank: number; gene: string; status: string; trust_boundary: string; score: number;
    stim_max_de: number; strongest_condition: string; rest_de: number; k562_de: number | null;
    rpe1_de: number | null; known_regulon_targets: number; rationale: string; assay: string;
    priority_lane: string; primary_readout: string; why_interesting: string; main_risk: string;
    what_would_weaken: string; review_summary: string;
  }[];
};
type CampaignReview = {
  title: string;
  status: string;
  trust_boundary: string;
  acceptance: boolean;
  campaign_id: string;
  candidate_count: number;
  top_gene: string;
  lane_counts: Record<string, number>;
  audit_questions: { question: string; field: string; pass_condition: string }[];
  rows: {
    rank: number; gene: string; status: string; trust_boundary: string; review_lane: string; decision: string;
    stimulated_signal: string; specificity: string; regulon_context: string; primary_readout: string;
    why_interesting: string; stop_rules: string[];
  }[];
};
type CampaignAgentProbe = {
  title: string;
  status: string;
  trust_boundary: string;
  acceptance: boolean;
  probe_id: string;
  campaign_id: string;
  model: string;
  candidate_count: number;
  tool_call_count: number;
  cost_usd: number;
  summary: Record<string, number>;
  rows: {
    rank: number; gene: string; status: string; trust_boundary: string; deterministic_lane: string;
    deterministic_decision: string; agent_recommendation: string; alignment: string; agent_rationale: string;
    stimulated_signal: string; specificity: string; stop_rules: string[];
  }[];
};
type CampaignTriage = {
  title: string;
  status: string;
  trust_boundary: string;
  acceptance: boolean;
  source_probe_id: string;
  campaign_id: string;
  summary: Record<string, number>;
  rows: {
    rank: number; gene: string; status: string; trust_boundary: string; alignment: string;
    deterministic_decision: string; agent_recommendation: string; triage_decision: string;
    stimulated_signal: string; specificity: string; assay_gate: string; reason_to_hold: string;
    stop_rules: string[]; agent_rationale: string;
  }[];
};
type LabPacket = {
  title: string;
  status: string;
  trust_boundary: string;
  acceptance: boolean;
  method: {
    negative_controls: string[]; positive_controls: string[]; exclusion_criteria: string[]; replay_links: string[];
  };
  candidates: {
    rank: number; gene: string; status: string; trust_boundary: string; intervention: string; sample: string;
    primary_readout: string; secondary_readout: string; decision_rule: string; negative_controls: string[];
    positive_controls: string[]; exclusion_criteria: string[]; replay_links: string[]; stim_max_de: number;
    strongest_condition: string; rest_de: number; k562_de: number | null; rpe1_de: number | null;
    known_regulon_targets: number; score: number; evidence: string[];
  }[];
};
type JudgePacket = {
  live_url: string;
  frontier_root: string;
  gate_commands: string[];
  demo_path: string[];
  public_data: string[];
  artifact_counts: {
    genes: number; edges: number; findings: number; receipts: number;
    agent_campaign_candidates: number; validation_candidates: number;
  };
  trust_boundary: { receipt_submission: string; model_moves_accepted_state: boolean };
};
type Data = {
  stats: { n_genes: number; n_perturbations: number; dist: Record<string, number>; n_edges: number };
  atlas: Node[]; out: Record<string, Edge[]>; in: Record<string, Edge[]>;
  contra: Contra[]; open: string[];
  surprises: { hidden_regulators: any[]; demoted_famous: any[]; untested_famous: any[] };
  finding_index?: FindingIndex | null;
  judge_packet?: JudgePacket | null;
  findings: Finding[]; citations: Record<string, Cite>;
  proposal?: { model: string; proposed: number; admitted: number; rejected: number; cost_usd: number;
    delta_id: string; items: { gene: string; verdict: string; rationale: string }[] } | null;
  agent?: { model: string; goal: string; rounds: number; tool_calls: number; cost_usd: number;
    delta_id: string; signer?: string; hypothesis?: { gene: string; hypothesis: string; evidence: string[]; why_novel: string } | null;
    transcript: { round: number; tool: string; input: any; result: any }[] } | null;
  receipts?: { id: string; status: string; replayability: string; kind: string; subject: string[];
    claim: string; accepted: boolean; producer: any; n_evidence: number; n_artifacts: number;
    verifier: string; replay: string; signer?: string }[];
  receipt_bridge?: {
    frontier_root: string; receipt_count: number; replay: string; mcp_command: string; exported_files: string[];
    protocol_path?: { step: number; method: string; action: string; result: string; accepted: boolean }[];
  };
  validation?: { gene: string; status: string; replayability: string; rest_de: string; stim8hr_de: string;
    stim48hr_de: string; stim_max_de: string; strongest_condition: string; k562_de: string;
    rpe1_de: string; known_regulon_targets: string; score: string; rationale: string;
    validation_assay: string }[];
  pggt1b_deep_dive?: PGGT1BDeepDive | null;
  agent_campaign?: AgentCampaign | null;
  agent_campaign_review?: CampaignReview | null;
  campaign_agent_probe?: CampaignAgentProbe | null;
  campaign_triage?: CampaignTriage | null;
  lab_packet?: LabPacket | null;
  demo: { text: string; gene: string; status: string; reason: string }[];
  phantom: any; models: any[];
  frontier: { root: string; signer: string; n_nodes: number; n_edges: number; n_contra: number; n_open: number; n_findings: number };
};

const CONDS = ["Rest", "Stim8hr", "Stim48hr"];
const CL = ["R", "8", "48"];
const CLASS: Record<string, [string, string]> = {
  constitutive_regulator: ["var(--moss)", "constitutive regulator"],
  condition_specific_regulator: ["var(--field-blue)", "condition-specific regulator"],
  reproduced_non_regulator: ["var(--stone)", "reproduced non-regulator"],
  unverifiable_no_kd: ["var(--brass)", "couldn’t test (no knockdown)"],
  off_target: ["var(--cinnabar)", "off-target"],
};
const STA: Record<string, string> = {
  regulator_major: "var(--moss)", regulator_minor: "var(--terrain-green)", regulator_weak: "var(--stone)",
  no_effect: "var(--ink-4)", no_knockdown: "var(--brass)", off_target: "var(--cinnabar)",
};
const DEMOC: Record<string, string> = {
  supported: "var(--moss)", refuted: "var(--cinnabar)", unsupported: "var(--cinnabar)",
  needs_qualification: "var(--brass)", asserted: "var(--stone)",
};
const fmt = (n: number) => n.toLocaleString();

const NAV = [
  { k: "overview", label: "Overview", icon: LayoutGrid },
  { k: "atlas", label: "Atlas", icon: Rows3 },
  { k: "network", label: "Network", icon: Share2 },
  { k: "frontier", label: "Frontier", icon: Waypoints },
  { k: "findings", label: "Findings", icon: Telescope },
  { k: "agent", label: "Agent", icon: Bot },
];

export default function Page() {
  const [d, setD] = useState<Data | null>(null);
  const [err, setErr] = useState(false);
  const [tab, setTab] = useState("overview");
  const [q, setQ] = useState("");
  const [gene, setGene] = useState<string | null>(null);
  const [focus, setFocus] = useState<string>("");
  const { resolvedTheme } = useTheme();
  const dark = resolvedTheme === "dark";
  useEffect(() => {
    fetch("/data/frontier.json")
      .then((r) => { if (!r.ok) throw new Error(String(r.status)); return r.json(); })
      .then((x: Data) => {
        setD(x);
        const hub = [...x.atlas].sort((a, b) => b.od - a.od)[0];
        setFocus(x.out["VAV1"] ? "VAV1" : hub ? hub.g : "VAV1");
      })
      .catch(() => setErr(true));
  }, []);
  const node = useMemo(() => (d && gene ? d.atlas.find((n) => n.g === gene) : null), [d, gene]);
  const label = NAV.find((n) => n.k === tab)?.label ?? "";

  const goSearch = () => { setTab("atlas"); setTimeout(() => document.getElementById("gene-search")?.focus(), 60); };

  return (
    <SidebarProvider>
      <Sidebar variant="inset">
        <SidebarHeader>
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 8px" }}>
            <span style={{ width: 9, height: 9, borderRadius: 999, background: "var(--brass-gold)",
              boxShadow: "0 0 0 3px color-mix(in oklab, var(--brass-gold) 22%, transparent)" }} />
            <span className="h2-app" style={{ fontSize: 15 }}>Prospect</span>
          </div>
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu>
                {NAV.map((n) => {
                  const Icon = n.icon;
                  return (
                    <SidebarMenuItem key={n.k}>
                      <SidebarMenuButton isActive={tab === n.k} tooltip={n.label}
                        onClick={() => setTab(n.k)} className="h-8 fz-sm">
                        <Icon aria-hidden strokeWidth={1.75} />
                        <span className="min-w-0 flex-1 truncate">{n.label}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
        <SidebarFooter>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "4px 6px" }}>
            <span className="t-caption" style={{ display: "inline-flex", alignItems: "center", gap: 5 }}>
              <ShieldCheck size={13} style={{ color: "var(--moss)" }} /> {d ? `signed · ${d.frontier.signer}` : "signed"}
            </span>
            <ThemeToggle />
          </div>
        </SidebarFooter>
      </Sidebar>

      <SidebarInset>
        <header style={{ display: "flex", alignItems: "center", gap: 10, height: 48, padding: "0 16px",
          borderBottom: "1px solid var(--header-border)", position: "sticky", top: 0, zIndex: 20,
          background: "color-mix(in oklab, var(--header-bg) 88%, transparent)", backdropFilter: "blur(8px)" }}>
          <SidebarTrigger className="btn btn-ghost btn-sm" />
          <span className="t-body-sm" style={{ color: "var(--ink-3)" }}>Prospect</span>
          <span className="t-body-sm" style={{ color: "var(--ink-4)" }}>/</span>
          <span className="t-body-sm" style={{ color: "var(--ink)", fontWeight: 600 }}>{label}</span>
          <button onClick={goSearch} className="btn btn-secondary btn-sm" style={{ marginLeft: "auto" }}>
            <Search /> <span className="fz-xs">Search a gene</span>
          </button>
        </header>

        <main className="app-main" style={{ padding: "26px 28px 72px", maxWidth: "78rem", width: "100%", margin: "0 auto" }}>
          {err ? (
            <div style={{ display: "grid", gap: 8, maxWidth: "48ch", paddingTop: 40 }}>
              <div className="h2-app">The frontier didn’t load.</div>
              <p className="t-body-sm" style={{ color: "var(--ink-3)" }}>
                Couldn’t fetch the signed data. Check your connection and reload.
              </p>
              <button onClick={() => location.reload()} className="btn btn-secondary btn-sm" style={{ justifySelf: "start", marginTop: 4 }}>Reload</button>
            </div>
          ) : !d ? (
            <div style={{ display: "grid", gap: 26 }} aria-busy="true">
              <div style={{ display: "grid", gap: 14 }}>
                <div className="skeleton" style={{ height: 12, width: 220, borderRadius: 4 }} />
                <div className="skeleton" style={{ height: 56, width: "min(620px, 90%)", borderRadius: 8 }} />
                <div className="skeleton" style={{ height: 56, width: "min(520px, 80%)", borderRadius: 8 }} />
              </div>
              <div className="skeleton" style={{ height: 150, borderRadius: 12 }} />
              <div style={{ display: "flex", gap: 44 }}>
                {[0, 1, 2, 3].map((i) => <div key={i} className="skeleton" style={{ height: 44, width: 96, borderRadius: 6 }} />)}
              </div>
            </div>
          ) : (
            <>
              {tab === "overview" && <Overview d={d} setTab={setTab} />}
              {tab === "atlas" && <Atlas d={d} q={q} setQ={setQ} onGene={setGene} />}
              {tab === "network" && <NetworkView d={d} focus={focus} setFocus={setFocus} dark={dark} onGene={setGene} />}
              {tab === "frontier" && <Frontier d={d} onGene={setGene} />}
              {tab === "findings" && <Findings d={d} onGene={setGene} />}
              {tab === "agent" && <AgentView d={d} onGene={setGene} />}
            </>
          )}
        </main>
      </SidebarInset>

      {node && d && <Peek node={node} d={d} onClose={() => setGene(null)} />}
    </SidebarProvider>
  );
}

function Overview({ d, setTab }: { d: Data; setTab: (tab: string) => void }) {
  const p = d.phantom, dist = d.stats.dist;
  const order = ["constitutive_regulator", "condition_specific_regulator", "reproduced_non_regulator", "unverifiable_no_kd"];
  const demoClaims = [...d.demo].sort((a, b) => {
    const rank: Record<string, number> = { unsupported: 0, refuted: 1, needs_qualification: 2, asserted: 3, supported: 4 };
    return (rank[a.status] ?? 9) - (rank[b.status] ?? 9);
  });
  const rate = p?.checkable ? Math.round((p.refuted / p.checkable) * 100) : null;
  return (
    <div style={{ display: "grid", gap: 26 }}>
      <header className="detail-hero" style={{ paddingBottom: 4 }}>
        <div className="t-label" style={{ marginBottom: 8 }}>Computationally reproduced regulatory frontier · CD4⁺ T cells</div>
        <h1 className="t-display" style={{ maxWidth: "18ch" }}>What actually regulates a human T cell.</h1>
        <p className="reading" style={{ marginTop: 12, maxWidth: "58ch", fontSize: "1rem" }}>
          A linked, human-signed graph of gene regulation. Every node and edge is re-derived from the released
          CRISPRi Perturb-seq data, never from a model. AI can assert a claim about any gene in seconds. Here
          you see only what the data holds.
        </p>
      </header>

      {rate != null && (
        <div className="card-paper" style={{ padding: "22px 24px", background: "var(--lacquer)", border: "none" }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 16, flexWrap: "wrap" }}>
            <div className="stat-figure" style={{ fontSize: "3rem", color: "var(--lantern)" }}>{rate}%</div>
            <div className="t-lede" style={{ color: "var(--ink-on)", fontSize: "1.15rem", maxWidth: "40ch" }}>
              of confident AI “major regulator” claims are contradicted by the measured data.
            </div>
          </div>
          <p className="t-body-sm" style={{ color: "var(--stone)", marginTop: 10, maxWidth: "72ch" }}>
            {p.models ? `Across ${p.models} frontier models` : "Across frontier models"} on one frozen sample,
            {" "}{p.refuted} of {fmt(p.checkable)} verifiable claims were wrong. Claims the screen couldn’t test
            (no knockdown) are excluded, not counted against the model.
          </p>
          {p.effector_total > 0 && (
            <div style={{ marginTop: 14, paddingTop: 14, borderTop: "1px solid color-mix(in oklab, var(--stone) 30%, transparent)" }}>
              <p className="t-body-sm" style={{ color: "var(--ink-on)", margin: 0, maxWidth: "72ch" }}>
                And on the <b style={{ color: "var(--lantern)" }}>{p.effector_total} genes the field targets most</b>,
                the checkpoints and cytokines like PD-1, TIM-3, IL-2, models called them a major regulator{" "}
                <b style={{ color: "var(--lantern)" }}>{p.effector_overclaimed}</b> times.{" "}
                The data shows near-zero transcriptional change: they are effectors, not drivers (Finding 02).
              </p>
            </div>
          )}
        </div>
      )}

      <div style={{ display: "flex", gap: 44, flexWrap: "wrap", padding: "18px 2px",
        borderTop: "1px solid var(--rule)", borderBottom: "1px solid var(--rule)" }}>
        {([
          [d.stats.n_genes, "genes mapped", "var(--ink)"],
          [d.stats.n_edges, "regulatory edges", "var(--moss)"],
          [(dist.constitutive_regulator || 0) + (dist.condition_specific_regulator || 0), "reproduced regulators", "var(--ink)"],
          [d.frontier.n_contra, "contradictions", "var(--cinnabar)"],
        ] as [number, string, string][]).map(([n, label, tone]) => (
          <div key={label}>
            <div className="stat-figure" style={{ color: tone, fontSize: "1.7rem", lineHeight: 1 }}>{fmt(n)}</div>
            <div className="t-label" style={{ marginTop: 6 }}>{label}</div>
          </div>
        ))}
      </div>

      <section style={{ display: "grid", gap: 12 }}>
        <h2 className="h2-app">Reproduced regulatory state across the genome</h2>
        <div style={{ display: "flex", height: 12, borderRadius: 6, overflow: "hidden" }}>
          {order.map((k) => <div key={k} style={{ flex: dist[k] || 0, background: CLASS[k][0] }} />)}
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 16 }}>
          {order.map((k) => (
            <span key={k} className="t-body-sm" style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
              <span style={{ width: 10, height: 10, borderRadius: 3, background: CLASS[k][0] }} />
              {CLASS[k][1]} · {fmt(dist[k] || 0)}
            </span>
          ))}
        </div>
      </section>

      <section style={{ display: "grid", gap: 10 }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Opening claim checks</div>
          <p className="t-body-sm" style={{ margin: 0, maxWidth: "70ch" }}>
            Start with claims a model can assert quickly. The checker keeps each verdict typed and grounded in the frozen table.
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 10 }}>
          {demoClaims.slice(0, 3).map((x) => (
            <div key={`${x.gene}-${x.status}`} style={{ padding: "12px 14px", border: "1px solid var(--rule)", borderRadius: "var(--radius-md)",
              background: "var(--paper-raised)", display: "grid", gap: 8 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                <span className="t-mono" style={{ fontWeight: 700 }}>{x.gene}</span>
                <span className="chip" style={{ ["--tone" as any]: DEMOC[x.status] }}>{x.status.replace(/_/g, " ")}</span>
              </div>
              <p className="t-body-sm" style={{ margin: 0, color: "var(--ink)" }}>{x.text}</p>
              <p className="t-caption" style={{ margin: 0, color: "var(--ink-3)" }}>{x.reason}</p>
            </div>
          ))}
        </div>
      </section>

      {d.judge_packet && <JudgePacketCard packet={d.judge_packet} setTab={setTab} />}

      {d.proposal && (
        <section style={{ display: "grid", gap: 10 }}>
          <h2 className="h2-app">Claude proposes, the frozen verifier decides</h2>
          <p className="t-body-sm" style={{ maxWidth: "68ch", marginTop: -2 }}>
            Claude ({d.proposal.model.replace("claude-", "").replace(/-/g, " ")}) proposed{" "}
            {d.proposal.proposed} candidate regulators. The frozen verifier admitted{" "}
            <b style={{ color: "var(--moss)" }}>{d.proposal.admitted}</b> and rejected{" "}
            <b style={{ color: "var(--cinnabar)" }}>{d.proposal.rejected}</b>, with no model in the trust path.
          </p>
          <div className="card-paper" style={{ padding: 0, overflow: "hidden" }}>
            {d.proposal.items.map((p, i) => {
              const admit = p.verdict === "supported";
              const tone = admit ? "var(--moss)" : p.verdict === "needs_qualification" ? "var(--brass)" : "var(--cinnabar)";
              const lab = admit ? "admit" : p.verdict === "needs_qualification" ? "qualify" : "reject";
              return (
                <div key={i} style={{ display: "grid", gridTemplateColumns: "72px 84px 1fr", gap: 10, alignItems: "center",
                  padding: "7px 14px", borderTop: i ? "1px solid var(--rule-faint)" : "none" }}>
                  <span className="chip" style={{ ["--tone" as any]: tone, justifySelf: "start" }}>{lab}</span>
                  <span className="t-mono" style={{ fontWeight: 650 }}>{p.gene}</span>
                  <span className="t-body-sm" style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", color: "var(--ink-3)" }}>{p.rationale}</span>
                </div>
              );
            })}
          </div>
          <p className="t-caption" style={{ marginTop: 8 }}>
            Signed delta <span className="t-mono" style={{ color: "var(--gold-ink)" }}>{d.proposal.delta_id}</span>.
            Claude is useful at proposing; the admission decision stays frozen re-derivation plus a human key.
          </p>
        </section>
      )}

      {d.models.length > 0 && (
        <section style={{ display: "grid", gap: 10 }}>
          <h2 className="h2-app">The same blind test, across model tiers</h2>
          <p className="t-body-sm" style={{ maxWidth: "66ch", marginTop: -2 }}>
            The cost of generating the claims is trivial and the rate at which they fail the data barely moves.
            Verification is the bottleneck, not generation.
          </p>
          <div className="card-paper" style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", minWidth: 520, borderCollapse: "collapse" }}>
              <thead>
                <tr className="t-label">
                  {["model", "cost", "verifiable", "contradicted", "effectors overclaimed"].map((h) => (
                    <th key={h} style={{ textAlign: "left", padding: "10px 14px", borderBottom: "1px solid var(--rule)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="t-mono" style={{ fontSize: 13 }}>
                {d.models.map((m) => (
                  <tr key={m.tag} style={{ borderTop: "1px solid var(--rule-faint)" }}>
                    <td style={{ padding: "9px 14px", fontWeight: 600 }}>{m.label}</td>
                    <td style={{ padding: "9px 14px" }}>${m.cost_usd.toFixed(3)}</td>
                    <td style={{ padding: "9px 14px" }}>{m.checkable}</td>
                    <td style={{ padding: "9px 14px", color: "var(--cinnabar)", fontWeight: 600 }}>
                      {m.refuted_rate != null ? Math.round(m.refuted_rate * 100) + "%" : "·"}
                    </td>
                    <td style={{ padding: "9px 14px", color: "var(--cinnabar)" }}>
                      {m.effector_total ? `${m.effector_overclaimed}/${m.effector_total}` : "·"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}

function JudgePacketCard({ packet, setTab }: { packet: JudgePacket; setTab: (tab: string) => void }) {
  const counts = packet.artifact_counts;
  return (
    <section className="card-paper" style={{ padding: "16px 18px", display: "grid", gap: 12 }}>
      <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <div style={{ minWidth: 240, flex: 1 }}>
          <div className="t-label" style={{ marginBottom: 5 }}>Judge packet</div>
          <p className="t-body-sm" style={{ margin: 0, maxWidth: "72ch" }}>
            One manifest for the replay path: signed root, gate commands, public data endpoints,
            receipt bridge, PGGT1B packet, and campaign leaderboard.
          </p>
        </div>
        <a className="btn btn-secondary btn-sm" href="/data/judge_packet.json" target="_blank" rel="noreferrer">
          JSON <ExternalLink size={13} />
        </a>
      </div>
      <div style={{ display: "flex", gap: 18, flexWrap: "wrap", alignItems: "baseline" }}>
        {[
          [fmt(counts.findings), "findings"],
          [fmt(counts.receipts), "receipts"],
          [fmt(counts.agent_campaign_candidates), "campaign rows"],
          [fmt(counts.validation_candidates), "wet-lab rows"],
        ].map(([value, label]) => (
          <div key={label}>
            <div className="t-mono" style={{ fontSize: 18, fontWeight: 700 }}>{value}</div>
            <div className="t-label" style={{ marginTop: 3 }}>{label}</div>
          </div>
        ))}
        <div style={{ marginLeft: "auto" }} className="t-caption">
          root <span className="t-mono" style={{ color: "var(--gold-ink)" }}>{packet.frontier_root}</span><br />
          receipt submission: {packet.trust_boundary.receipt_submission.replace(/_/g, " ")}
        </div>
      </div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {packet.gate_commands.slice(0, 3).map((cmd) => (
          <span key={cmd} className="t-mono fz-2xs" style={{ padding: "4px 7px", borderRadius: 5,
            background: "var(--paper-recessed)", border: "1px solid var(--rule-faint)" }}>{cmd}</span>
        ))}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap",
        paddingTop: 2, borderTop: "1px solid var(--rule-faint)" }}>
        <span className="t-label" style={{ marginRight: 2 }}>Demo path</span>
        <button type="button" className="btn btn-secondary btn-sm"
          title={packet.demo_path[1]} onClick={() => setTab("findings")}>
          Findings
        </button>
        <button type="button" className="btn btn-secondary btn-sm"
          title={packet.demo_path[2]} onClick={() => setTab("frontier")}>
          Frontier
        </button>
        <button type="button" className="btn btn-secondary btn-sm"
          title={packet.demo_path[3]} onClick={() => setTab("agent")}>
          Agent
        </button>
      </div>
    </section>
  );
}

function Atlas({ d, q, setQ, onGene }: { d: Data; q: string; setQ: (s: string) => void; onGene: (g: string) => void }) {
  const maxdn = (g: Node) => Math.max(0, ...CONDS.map((c) => (g.C[c] ? g.C[c].dn : 0)));
  const list = useMemo(() => {
    const Q = q.trim().toUpperCase();
    return d.atlas.filter((g) => !Q || g.g.toUpperCase().includes(Q)).sort((a, b) => maxdn(b) - maxdn(a)).slice(0, 120);
  }, [d, q]);
  return (
    <div>
      <h2 className="h1-display" style={{ marginBottom: 4 }}>Atlas</h2>
      <p className="t-body-sm" style={{ marginBottom: 14, maxWidth: "62ch" }}>
        Search a gene. Each row shows its frozen-data class and per-condition status (R rest · 8 8h · 48 48h stim).
        Open a gene for its regulatory neighborhood, what it regulates, and the claims the data refused.
      </p>
      <input id="gene-search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search a gene (VAV1, BCL10, PDCD1)…"
        style={{ width: 320, height: 36, padding: "0 12px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border)",
          background: "var(--paper)", color: "var(--ink)", marginBottom: 14 }} className="t-body" />
      <div className="card-paper" style={{ overflow: "hidden", padding: 0 }}>
        {list.map((g, i) => {
          const c = CLASS[g.cls];
          return (
            <button key={g.g} onClick={() => onGene(g.g)} className="state-row"
              style={{ display: "flex", alignItems: "center", gap: 12, width: "100%", textAlign: "left",
                padding: "9px 14px", borderTop: i ? "1px solid var(--rule-faint)" : "none", background: "transparent",
                ["--state" as any]: c[0] } as any}>
              <span className="t-mono" style={{ width: 92, fontWeight: 650 }}>{g.g}</span>
              <span className="chip" style={{ ["--tone" as any]: c[0] }}>{c[1]}</span>
              <span style={{ display: "flex", gap: 4, marginLeft: "auto" }}>
                {CONDS.map((cd, k) => {
                  const v = g.C[cd];
                  return <span key={cd} title={v ? `${cd}: ${v.s}, ${v.de} DE` : cd}
                    style={{ width: 30, textAlign: "center", fontSize: 11, fontWeight: 600, color: "var(--ink-on)",
                      borderRadius: 5, padding: "3px 0", background: v ? STA[v.s] || "var(--stone)" : "var(--paper-recessed)" }}>{CL[k]}</span>;
                })}
              </span>
            </button>
          );
        })}
      </div>
      <div className="t-caption" style={{ marginTop: 10 }}>showing {list.length} · sorted by downstream reach</div>
    </div>
  );
}

function NetworkView({ d, focus, setFocus, dark, onGene }:
  { d: Data; focus: string; setFocus: (g: string) => void; dark: boolean; onGene: (g: string) => void }) {
  const [fq, setFq] = useState("");
  const out = d.out[focus] || [], inn = d.in[focus] || [];
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const g = d.atlas.find((n) => n.g === fq.trim().toUpperCase());
    if (g) { setFocus(g.g); setFq(""); }
  };
  return (
    <div>
      <h2 className="h1-display" style={{ marginBottom: 6 }}>Regulatory network</h2>
      <p className="t-body-sm" style={{ marginBottom: 14, maxWidth: "66ch" }}>
        The neighborhood around <b>{focus}</b>, {out.length} genes it regulates, {inn.length} that regulate it, and the
        cross-links between them. Edges by direction (<span style={{ color: "var(--moss)" }}>up</span> /{" "}
        <span style={{ color: "var(--cinnabar)" }}>down</span>). Click any node to re-center the graph on it.
      </p>
      <form onSubmit={submit} style={{ display: "flex", gap: 8, marginBottom: 12, alignItems: "center", flexWrap: "wrap" }}>
        <input value={fq} onChange={(e) => setFq(e.target.value)} placeholder={`Center on a gene (now: ${focus})`}
          className="t-body" style={{ width: 300, height: 34, padding: "0 12px", borderRadius: "var(--radius-sm)",
            border: "1px solid var(--border)", background: "var(--paper)", color: "var(--ink)" }} />
        <button className="btn btn-secondary btn-sm" type="submit">Re-center</button>
        <button className="btn btn-ghost btn-sm" type="button" onClick={() => onGene(focus)}>Open {focus} details</button>
      </form>
      {focus && <GraphView data={d} focus={focus} onFocus={setFocus} dark={dark} />}
      <div className="t-caption" style={{ marginTop: 10, display: "flex", gap: 16, flexWrap: "wrap" }}>
        <span><i style={{ display: "inline-block", width: 9, height: 9, borderRadius: 999, background: "#c99a3a", marginRight: 5 }} />focus gene</span>
        <span><i style={{ display: "inline-block", width: 9, height: 9, borderRadius: 999, background: "#4e7a44", marginRight: 5 }} />regulator</span>
        <span><i style={{ display: "inline-block", width: 9, height: 9, borderRadius: 999, background: "#8a8272", marginRight: 5 }} />target</span>
        <span>node size = downstream reach · edges sliced live from the released DE matrix</span>
      </div>
    </div>
  );
}

const RCPT_STATUS: Record<string, [string, string]> = {
  computationally_reproduced: ["var(--moss)", "reproduced"],
  evidence_attached: ["var(--brass)", "evidence attached"],
  contradicted: ["var(--cinnabar)", "contradicted"],
  refuted: ["var(--cinnabar)", "refuted"],
  claimed: ["var(--stone)", "claimed"],
};
const BOUNDARY = ["Activity", "Receipt", "Proposal", "Review", "Verification", "Accepted", "State"];
const BRIDGE_METHOD_ORDER = [
  "prospect.receipt.schema",
  "prospect.receipt.validate",
  "prospect.receipt.submit",
];

function Receipts({ receipts, bridge }: { receipts: NonNullable<Data["receipts"]>; bridge?: Data["receipt_bridge"] }) {
  return (
    <div style={{ display: "grid", gap: 12 }}>
      <div>
        <div className="t-label" style={{ marginBottom: 4 }}>How activity becomes state</div>
        <p className="t-body-sm" style={{ maxWidth: "70ch", margin: 0 }}>
          A model can assert anything in a second. A receipt is the portable proposal that records what
          was claimed, which frozen artifacts it stands on, which facts a verifier confirms, how to replay
          it, and whether a human accepted it. Any producer can emit one; the same frozen gate decides.
        </p>
      </div>
      <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: 4, padding: "10px 0" }}>
        {BOUNDARY.map((s, i) => (
          <span key={s} style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
            <span className="t-mono fz-2xs" style={{ padding: "3px 8px", borderRadius: 5,
              background: s === "Receipt" ? "var(--gold-tint, var(--state-open-tint))" : "var(--paper-recessed)",
              color: s === "Receipt" ? "var(--gold-ink)" : "var(--ink-3)", fontWeight: s === "Receipt" ? 700 : 500,
              border: s === "Receipt" ? "1px solid var(--brass-gold)" : "1px solid var(--rule-faint)" }}>{s}</span>
            {i < BOUNDARY.length - 1 && <span className="t-caption" style={{ color: "var(--ink-4)" }}>›</span>}
          </span>
        ))}
      </div>
      {bridge && (
        <div className="card-paper" style={{ padding: "12px 14px", display: "grid", gap: 12 }}>
          <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
            <div style={{ minWidth: 220, flex: 1 }}>
              <div className="t-label">Executable bridge path</div>
              <p className="t-body-sm" style={{ margin: "4px 0 0", color: "var(--ink-3)" }}>
                An external workbench can discover the schema, validate a receipt, and submit it as proposal only.
                Accepted state still requires the human key.
              </p>
            </div>
            <a className="btn btn-secondary btn-sm" href="/data/receipt_bridge/receipt_contract.json" target="_blank" rel="noreferrer">
              Contract <ExternalLink size={13} />
            </a>
            <a className="btn btn-secondary btn-sm" href="/data/receipt_bridge/receipt_manifest.json" target="_blank" rel="noreferrer">
              Manifest <ExternalLink size={13} />
            </a>
            <a className="btn btn-secondary btn-sm" href="/data/receipt_bridge/receipt_bundle.json" target="_blank" rel="noreferrer">
              Bundle <ExternalLink size={13} />
            </a>
            <span className="t-caption" style={{ color: "var(--ink-3)" }}>{bridge.receipt_count} receipts · {bridge.mcp_command}</span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: 8 }}>
            {(bridge.protocol_path || BRIDGE_METHOD_ORDER.map((method, i) => ({
              step: i + 1, method, action: "", result: method.endsWith("submit") ? "proposal_only" : "", accepted: false,
            }))).map((step) => (
              <div key={step.method} style={{ padding: "8px 9px", border: "1px solid var(--rule-faint)",
                borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)", display: "grid", gap: 4 }}>
                <div className="t-caption" style={{ color: "var(--ink-4)" }}>step {step.step}</div>
                <div className="t-mono fz-2xs" style={{ color: "var(--field-blue)", fontWeight: 700 }}>{step.method}</div>
                <div className="t-body-sm" style={{ color: "var(--ink-3)" }}>
                  {step.result === "proposal_only" ? "submit returns proposal only" : step.action}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      <div className="card-paper" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr auto auto", gap: 12, padding: "6px 14px" }}>
          {["claim", "status", "replay"].map((h, i) => (
            <span key={h} className="t-label" style={{ color: "var(--ink-3)", textAlign: i === 0 ? "left" : "right" }}>{h}</span>
          ))}
        </div>
        {receipts.map((r) => {
          const [tone, label] = RCPT_STATUS[r.status] || ["var(--stone)", r.status];
          return (
            <div key={r.id} style={{ display: "grid", gridTemplateColumns: "1fr auto auto", gap: 12, alignItems: "center",
              padding: "9px 14px", borderTop: "1px solid var(--rule-faint)" }}>
              <div style={{ minWidth: 0 }}>
                <div style={{ display: "flex", gap: 8, alignItems: "baseline", flexWrap: "wrap" }}>
                  <span className="t-mono fz-2xs" style={{ color: "var(--ink-4)" }}>{r.id}</span>
                  <span className="t-body-sm" style={{ fontWeight: 600 }}>{r.kind === "hypothesis" ? "hypothesis" : r.kind.replace(/_/g, " ")}</span>
                  <span className="t-caption" style={{ color: "var(--ink-3)" }}>· {r.producer?.kind === "autonomous_agent" ? `agent (${r.n_evidence} reproduced facts)` : `${r.n_evidence} atoms · ${r.n_artifacts} artifacts`}{r.accepted ? ` · signed ${r.signer}` : ""}</span>
                </div>
                <div className="t-body-sm" style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", color: "var(--ink-2)" }}>{r.claim}</div>
              </div>
              <div style={{ textAlign: "right", display: "grid", gap: 2 }}>
                <span className="chip" style={{ ["--tone" as any]: tone, justifySelf: "end" }}>{label}</span>
                <span className="t-caption" style={{ color: "var(--ink-3)" }}>{r.replayability}</span>
              </div>
              <span className="t-mono fz-2xs" style={{ textAlign: "right", color: "var(--ink-3)" }}>{r.replay}</span>
            </div>
          );
        })}
      </div>
      <p className="t-caption" style={{ margin: 0 }}>
        The status never collapses to a generic proof label. A hypothesis to test stays <b>evidence attached</b>; only what
        re-derives from frozen data is <b>reproduced</b>; where the data disagrees it is <b>contradicted</b>. No model in the trust path.
      </p>
    </div>
  );
}

function Frontier({ d, onGene }: { d: Data; onGene: (g: string) => void }) {
  return (
    <div style={{ display: "grid", gap: 24 }}>
      <div>
        <h2 className="h1-display" style={{ marginBottom: 6 }}>The frontier</h2>
        <p className="reading" style={{ maxWidth: "58ch", fontSize: "1rem" }}>
          The signed graph is accepted state, re-derived from frozen data and signed by a human. Contradictions
          and open questions are kept as first-class, citable terrain.
        </p>
      </div>
      <div style={{ display: "flex", gap: 26, flexWrap: "wrap", alignItems: "center" }}>
        <div><div className="stat-figure">{fmt(d.frontier.n_edges)}</div><div className="t-label">reproduced edges</div></div>
        <div><div className="stat-figure" style={{ color: "var(--cinnabar)" }}>{fmt(d.frontier.n_contra)}</div><div className="t-label">contradictions</div></div>
        <div><div className="stat-figure" style={{ color: "var(--brass)" }}>{fmt(d.frontier.n_open)}</div><div className="t-label">open questions</div></div>
        <div style={{ marginLeft: "auto", textAlign: "right" }} className="t-caption">
          signed <span className="t-mono" style={{ color: "var(--gold-ink)" }}>{d.frontier.root}</span><br />
          by {d.frontier.signer} · no model in the trust path
        </div>
      </div>

      {d.receipts && d.receipts.length > 0 && <Receipts receipts={d.receipts} bridge={d.receipt_bridge} />}

      <div>
        <div className="t-label" style={{ marginBottom: 8 }}>Contradictions, where AI claims meet the data</div>
        <div className="card-paper" style={{ padding: 0, overflow: "hidden" }}>
          {d.contra.slice(0, 60).map((x, i) => (
            <button key={i} onClick={() => onGene(x.gene)} className="state-row"
              style={{ display: "flex", alignItems: "center", gap: 10, width: "100%", textAlign: "left",
                padding: "8px 14px", borderTop: i ? "1px solid var(--rule-faint)" : "none", background: "transparent",
                ["--state" as any]: "var(--cinnabar)" } as any}>
              <span className="t-mono" style={{ width: 84, fontWeight: 650 }}>{x.gene}</span>
              <span className="chip" style={{ ["--tone" as any]: "var(--cinnabar)" }}>{x.verdict}</span>
              <span className="t-body-sm" style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {x.claimant}: “{x.claim}”
              </span>
            </button>
          ))}
        </div>
      </div>
      <div>
        <div className="t-label" style={{ marginBottom: 6 }}>Open frontier, the screen couldn’t test these</div>
        <p className="t-body-sm" style={{ marginBottom: 10, maxWidth: "64ch" }}>
          Knockdown never succeeded, so the data is silent, honest gaps, and the demand surface for the next experiments.
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
          {d.open.map((g) => <span key={g} className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>{g}</span>)}
        </div>
      </div>
    </div>
  );
}

const FINDING_META: Record<string, { n: string; title: string; tone: string }> = {
  activation_module: { n: "01", title: "The activation module, rebuilt from perturbation", tone: "var(--moss)" },
  regulator_vs_effector: { n: "02", title: "Regulator vs effector", tone: "var(--cinnabar)" },
  essentiality_artifact: { n: "03", title: "Reach is not regulation", tone: "var(--brass)" },
  cross_cell_type_transfer: { n: "04", title: "Verifier transfer, a second cell type", tone: "var(--field-blue)" },
  regulon_recovery: { n: "05", title: "Recovering known regulons from perturbation", tone: "var(--brass-gold)" },
};

function FindingHead({ f }: { f: Finding }) {
  const m = FINDING_META[f.kind];
  return (
    <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 8 }}>
      <span className="t-mono" style={{ fontSize: 13, color: m.tone, fontWeight: 700 }}>{m.n}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <span className="h2-app">{m.title}</span>
          <span className="chip" style={{ ["--tone" as any]: m.tone }}>{f.status}</span>
          <span className="t-mono fz-2xs" style={{ color: "var(--ink-4)" }}>{f.n_genes} genes · {f.cid}</span>
        </div>
        <p className="t-body-sm" style={{ marginTop: 6, maxWidth: "70ch" }}>{f.claim}</p>
      </div>
    </div>
  );
}

function EvRow({ cells, head }: { cells: ReactNode[]; head?: boolean }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "96px 1fr auto", gap: 12, alignItems: "center",
      padding: "6px 14px", borderTop: head ? "none" : "1px solid var(--rule-faint)" }}>
      {cells.map((c, i) => (
        <span key={i} className={head ? "t-label" : i === 0 ? "t-mono" : "t-body-sm"}
          style={{ fontWeight: !head && i === 0 ? 650 : undefined, textAlign: i === 2 ? "right" : "left",
            color: head ? "var(--ink-3)" : undefined }}>{c}</span>
      ))}
    </div>
  );
}

function ActivationEvidence({ f }: { f: Finding }) {
  const ex: Record<string, { rest_de: number; stim_max_de: number }> = f.evidence.canonical_exemplar || {};
  const rows = Object.entries(ex).sort((a, b) => b[1].stim_max_de - a[1].stim_max_de).slice(0, 12);
  return (
    <div className="card-paper" style={{ padding: 0, overflow: "hidden" }}>
      <EvRow head cells={["gene", "TCR-cascade component", "Rest → Stim (max) DE"]} />
      {rows.map(([g, v]) => (
        <EvRow key={g} cells={[g, "silent at rest, fires on stimulation",
          <span key="n"><b style={{ color: "var(--ink-4)" }}>{v.rest_de}</b> → <b style={{ color: "var(--moss)" }}>{fmt(v.stim_max_de)}</b></span>]} />
      ))}
    </div>
  );
}

function EffectorEvidence({ f, d, onGene }: { f: Finding; d: Data; onGene: (g: string) => void }) {
  const per: Record<string, { stim_condition: string; n_de: number }> = f.evidence.per_gene || {};
  // cited genes first (they carry the literature-vs-data contradiction), then the rest
  const cited = Object.keys(per).filter((g) => d.citations[g]).sort();
  const rest = Object.keys(per).filter((g) => !d.citations[g]).sort();
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div className="card-paper" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ display: "grid", gridTemplateColumns: "96px 1fr auto", gap: 12, padding: "6px 14px" }}>
          <span className="t-label" style={{ color: "var(--ink-3)" }}>gene</span>
          <span className="t-label" style={{ color: "var(--ink-3)" }}>the field calls it (cited)</span>
          <span className="t-label" style={{ color: "var(--ink-3)", textAlign: "right" }}>DE on KD</span>
        </div>
        {cited.map((g) => {
          const c = d.citations[g], p = per[g];
          return (
            <div key={g} style={{ display: "grid", gridTemplateColumns: "96px 1fr auto", gap: 12, alignItems: "center",
              padding: "7px 14px", borderTop: "1px solid var(--rule-faint)" }}>
              <button onClick={() => onGene(g)} className="t-mono" style={{ fontWeight: 650, textAlign: "left",
                background: "transparent", color: "var(--cinnabar)" }}>{g}</button>
              <span className="t-body-sm" style={{ minWidth: 0 }}>
                {c.canonical_role.split(":")[0]} ·{" "}
                <a href={`https://doi.org/${c.doi}`} target="_blank" rel="noreferrer"
                  className="t-caption" style={{ color: "var(--ink-3)", textDecoration: "none" }}>
                  {c.first_author} {c.year} <ExternalLink size={10} style={{ display: "inline", verticalAlign: "baseline" }} />
                </a>
              </span>
              <span className="t-mono fz-sm" style={{ textAlign: "right", fontWeight: 650, color: "var(--cinnabar)" }}>
                {p.n_de} <span className="t-caption">({p.stim_condition})</span>
              </span>
            </div>
          );
        })}
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, alignItems: "center" }}>
        <span className="t-caption">also effectors:</span>
        {rest.map((g) => (
          <button key={g} onClick={() => onGene(g)} className="chip"
            style={{ ["--tone" as any]: "var(--stone)", background: "transparent" }}>{g}</button>
        ))}
      </div>
    </div>
  );
}

function EssentialityEvidence({ f }: { f: Finding }) {
  const per: Record<string, { rest_de: number }> = f.evidence.per_gene || {};
  const gap = f.evidence.gap || {};
  const rows = Object.entries(per).sort((a, b) => b[1].rest_de - a[1].rest_de).slice(0, 10);
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div className="card-paper" style={{ padding: 0, overflow: "hidden" }}>
        <EvRow head cells={["gene", "general machinery, not immune biology", "Rest DE"]} />
        {rows.map(([g, v]) => (
          <EvRow key={g} cells={[g, "moves the transcriptome in a resting cell",
            <b key="n" style={{ color: "var(--brass)" }}>{fmt(v.rest_de)}</b>]} />
        ))}
      </div>
      <div className="card-paper" style={{ padding: "10px 15px", background: "var(--state-open-tint)" }}>
        <p className="t-body-sm" style={{ margin: 0 }}>
          The gap is decisive: machinery genes sit at Rest DE ≥ <b>{fmt(gap.machinery_rest_de_min ?? 0)}</b>; the
          activation module (Finding 01) tops out at Rest DE <b>{gap.activation_module_rest_de_max ?? 0}</b>. Nothing
          lands in between. Phase 3 tests this against a non-immune cell type.
        </p>
      </div>
    </div>
  );
}

function TransferEvidence({ f, onGene }: { f: Finding; onGene: (g: string) => void }) {
  const e = f.evidence;
  const med = e.median_k562_de || {};
  const per: Record<string, { marson: string; replogle: string; k562_de: number | null; finding: string }> = e.per_gene || {};
  const essRate = Math.round((e.essentiality_replication?.rate || 0) * 100);
  const actRate = Math.round((e.activation_specificity?.rate || 0) * 100);
  // recognizable exemplars: strongest housekeeping replications + iconic TCR genes inert in K562
  const house = (e.housekeeping_exemplar || []).slice(0, 4);
  const immune = (e.immune_exemplar || []).slice(0, 4);
  const Row = ({ g, tone }: { g: string; tone: string }) => (
    <div style={{ display: "grid", gridTemplateColumns: "96px 1fr auto", gap: 12, alignItems: "center",
      padding: "7px 14px", borderTop: "1px solid var(--rule-faint)" }}>
      <button onClick={() => onGene(g)} className="t-mono" style={{ fontWeight: 650, textAlign: "left", background: "transparent", color: tone }}>{g}</button>
      <span className="t-body-sm">T-cell regulator · {per[g].finding === "essentiality_artifact" ? "replicates in K562" : "inert in K562"}</span>
      <span className="t-mono fz-sm" style={{ textAlign: "right" }}>K562 {per[g].k562_de ?? "·"} DE</span>
    </div>
  );
  return (
    <div style={{ display: "grid", gap: 12 }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div className="card-paper" style={{ padding: "14px 16px" }}>
          <div className="stat-figure" style={{ color: "var(--brass)" }}>{med.essentiality_artifact ?? "·"}</div>
          <div className="t-label" style={{ marginTop: 4 }}>essentiality artifacts · median K562 DE</div>
          <div className="t-caption" style={{ marginTop: 6 }}>{essRate}% replicate, housekeeping, as predicted</div>
        </div>
        <div className="card-paper" style={{ padding: "14px 16px" }}>
          <div className="stat-figure" style={{ color: "var(--moss)" }}>{med.activation_module ?? "·"}</div>
          <div className="t-label" style={{ marginTop: 4 }}>activation module · median K562 DE</div>
          <div className="t-caption" style={{ marginTop: 6 }}>{actRate}% are K562-inert, T-cell-specific</div>
        </div>
      </div>
      <p className="t-body-sm" style={{ maxWidth: "72ch", margin: "2px 0" }}>
        The same major-regulator claim, run through <b>get_checker(&quot;marson&quot;)</b> and{" "}
        <b>get_checker(&quot;replogle&quot;)</b>, one verifier shape, two frozen datasets. Essentiality
        artifacts reshape the K562 transcriptome too (median {med.essentiality_artifact} DE); the activation
        module stays inert (median {med.activation_module}). The second dataset validates findings 01 and 03.
      </p>
      <div className="card-paper" style={{ padding: 0, overflow: "hidden" }}>
        {house.map((g: string) => <Row key={g} g={g} tone="var(--brass)" />)}
        {immune.map((g: string) => <Row key={g} g={g} tone="var(--moss)" />)}
      </div>
    </div>
  );
}

function RegulonEvidence({ f, onGene }: { f: Finding; onGene: (g: string) => void }) {
  const e = f.evidence;
  const recPct = Math.round((e.recovery_rate || 0) * 100);
  const dirPct = Math.round((e.directional_agreement || 0) * 100);
  const top: any[] = e.top_recovered || [];
  const wrong: any[] = e.wrong_direction_exemplars || [];
  return (
    <div style={{ display: "grid", gap: 12 }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
        <div className="card-paper" style={{ padding: "14px 16px" }}>
          <div className="stat-figure" style={{ color: "var(--moss)" }}>{e.pooled_fold_enrichment}×</div>
          <div className="t-label" style={{ marginTop: 4 }}>known targets enriched</div>
          <div className="t-caption" style={{ marginTop: 6 }}>among data edges · Fisher p≈{e.combined_p}</div>
        </div>
        <div className="card-paper" style={{ padding: "14px 16px" }}>
          <div className="stat-figure">{dirPct}%</div>
          <div className="t-label" style={{ marginTop: 4 }}>directional agreement</div>
          <div className="t-caption" style={{ marginTop: 6 }}>right sign, activator vs repressor</div>
        </div>
        <div className="card-paper" style={{ padding: "14px 16px" }}>
          <div className="stat-figure" style={{ color: "var(--cinnabar)" }}>{e.n_wrong_direction_edges}</div>
          <div className="t-label" style={{ marginTop: 4 }}>edges the data overrules</div>
          <div className="t-caption" style={{ marginTop: 6 }}>known sign contradicted</div>
        </div>
      </div>
      <p className="t-body-sm" style={{ maxWidth: "72ch", margin: "2px 0" }}>
        Each TF's CollecTRI literature regulon, checked against the genes its knockdown actually moved,
        over the {e.n_tfs_tested} TFs that are major regulators here. {e.n_recovered} clear significance
        on their own, including the Th1 and Th2 master factors TBX21 and GATA3. The frontier rebuilds
        known transcription-factor biology from perturbation alone, with no regulon supplied.
      </p>
      <div className="card-paper" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ display: "grid", gridTemplateColumns: "96px 1fr auto auto", gap: 12, padding: "6px 14px" }}>
          {["TF", "known regulon recovered", "enrichment", "sign"].map((h, i) => (
            <span key={h} className="t-label" style={{ color: "var(--ink-3)", textAlign: i > 1 ? "right" : "left" }}>{h}</span>
          ))}
        </div>
        {top.map((r) => (
          <div key={r.tf} style={{ display: "grid", gridTemplateColumns: "96px 1fr auto auto", gap: 12, alignItems: "center",
            padding: "7px 14px", borderTop: "1px solid var(--rule-faint)" }}>
            <button onClick={() => onGene(r.tf)} className="t-mono" style={{ fontWeight: 650, textAlign: "left", background: "transparent", color: "var(--moss)" }}>{r.tf}</button>
            <span className="t-body-sm">{r.overlap} of {r.known} known targets moved on knockdown</span>
            <span className="t-mono fz-sm" style={{ textAlign: "right", color: "var(--moss)" }}>{r.fold}×</span>
            <span className="t-mono fz-sm" style={{ textAlign: "right" }}>{r.dir_agree != null ? Math.round(r.dir_agree * 100) + "%" : "·"}</span>
          </div>
        ))}
      </div>
      {wrong.length > 0 && (
        <div>
          <div className="t-label" style={{ marginBottom: 6 }}>Where the data overrules the literature's sign</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {wrong.map((w, i) => (
              <span key={i} className="chip" style={{ ["--tone" as any]: "var(--cinnabar)" }}>
                {w.tf} {w.collectri === "activates" ? "activates" : "represses"} {w.target}?
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function AgentView({ d, onGene }: { d: Data; onGene: (g: string) => void }) {
  const a = d.agent;
  if (!a) return <div className="t-label">No agent run recorded.</div>;
  const h = a.hypothesis;
  const summarize = (tool: string, result: any) => {
    if (!result) return "";
    if (tool === "search_regulators") return `${(result.candidates || []).length} candidates`;
    if (tool === "check_regulator") return result.in_screen === false ? "not in screen" :
      `${result.class}, ${fmt(result.stim_max_de)} DE stim` + (result.is_canonical_Tcell_gene ? " · canonical" : "");
    if (tool === "cross_cell_type") return `K562 ${result.k562_de ?? "·"} DE → ${result.verdict}`;
    if (tool === "known_regulon") return result.is_known_TF_in_CollecTRI ? `known TF, ${result.n_known_targets} targets` : "no annotated regulon";
    return "";
  };
  return (
    <div style={{ display: "grid", gap: 24 }}>
      <div>
        <h2 className="h1-display" style={{ marginBottom: 6 }}>The agent</h2>
        <p className="reading" style={{ maxWidth: "62ch", fontSize: "1rem" }}>
          Claude ({a.model.replace("claude-", "").replace(/-/g, " ")}) pursues a research goal by calling
          frozen-data tools. Every fact it reasons over is a deterministic lookup against a released table,
          so it cannot hallucinate its evidence. It converges on a hypothesis; a human signs it.
        </p>
      </div>
      <div className="card-paper" style={{ padding: "14px 18px", background: "var(--lacquer)", border: "none" }}>
        <div className="t-label" style={{ color: "var(--stone)", marginBottom: 6 }}>Goal</div>
        <div className="t-body-sm" style={{ color: "var(--ink-on)" }}>{a.goal}</div>
        <div className="t-caption" style={{ color: "var(--stone)", marginTop: 8 }}>
          {a.tool_calls} frozen-data tool calls over {a.rounds} rounds · ${a.cost_usd}
        </div>
      </div>

      {h && (
        <div className="card-paper" style={{ padding: "18px 20px", borderColor: "var(--moss)" }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 10, flexWrap: "wrap", marginBottom: 6 }}>
            <span className="t-label" style={{ color: "var(--moss)" }}>Signed hypothesis</span>
            <button onClick={() => onGene(h.gene)} className="t-mono" style={{ fontSize: 17, fontWeight: 700, background: "transparent", color: "var(--ink)" }}>{h.gene}</button>
          </div>
          <p className="t-lede" style={{ fontSize: "1.05rem", marginBottom: 10 }}>{h.hypothesis}</p>
          <div className="t-label" style={{ marginBottom: 6 }}>Reproduced evidence</div>
          <ul style={{ margin: 0, paddingLeft: 0, listStyle: "none", display: "grid", gap: 4 }}>
            {h.evidence.map((e, i) => (
              <li key={i} className="t-body-sm" style={{ display: "flex", gap: 8 }}>
                <ShieldCheck size={14} style={{ color: "var(--moss)", flexShrink: 0, marginTop: 3 }} /> {e}
              </li>
            ))}
          </ul>
          <p className="t-caption" style={{ marginTop: 10 }}>
            <b>Why novel:</b> {h.why_novel}
          </p>
          <p className="t-caption" style={{ marginTop: 8 }}>
            signed delta <span className="t-mono" style={{ color: "var(--gold-ink)" }}>{a.delta_id}</span>
            {a.signer ? ` · accepted by ${a.signer}` : ""} · no model in the trust path
          </p>
        </div>
      )}

      {d.pggt1b_deep_dive && <PGGT1BDeepDiveCard dive={d.pggt1b_deep_dive} onGene={onGene} />}

      {d.agent_campaign && <AgentCampaignLeaderboard campaign={d.agent_campaign} onGene={onGene} />}

      {d.agent_campaign_review && <CampaignReviewAppendix review={d.agent_campaign_review} onGene={onGene} />}

      {d.campaign_agent_probe && <CampaignAgentProbe probe={d.campaign_agent_probe} onGene={onGene} />}

      {d.campaign_triage && <CampaignDisagreementTriage triage={d.campaign_triage} onGene={onGene} />}

      {d.lab_packet && <LabPacketCard packet={d.lab_packet} onGene={onGene} />}

      {d.validation && d.validation.length > 0 && (
        <ValidationShortlist rows={d.validation.slice(0, 8)} onGene={onGene} />
      )}

      <div>
        <div className="t-label" style={{ marginBottom: 8 }}>How it got there, every step a frozen-data tool call</div>
        <div className="card-paper" style={{ padding: 0, overflow: "hidden" }}>
          {a.transcript.map((t, i) => (
            <div key={i} style={{ display: "grid", gridTemplateColumns: "40px 1fr", gap: 10, alignItems: "center",
              padding: "7px 14px", borderTop: i ? "1px solid var(--rule-faint)" : "none" }}>
              <span className="t-mono fz-2xs" style={{ color: "var(--ink-4)" }}>r{t.round}</span>
              <div style={{ display: "flex", gap: 8, alignItems: "baseline", flexWrap: "wrap", minWidth: 0 }}>
                <span className="t-mono fz-sm" style={{ fontWeight: 650, color: "var(--field-blue)" }}>{t.tool}</span>
                {t.input?.gene && <button onClick={() => onGene(t.input.gene)} className="t-mono fz-sm" style={{ background: "transparent", color: "var(--ink)" }}>{t.input.gene}</button>}
                <span className="t-caption" style={{ color: "var(--ink-3)" }}>{summarize(t.tool, t.result)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function AgentCampaignLeaderboard({ campaign, onGene }: { campaign: AgentCampaign; onGene: (g: string) => void }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Agent campaign leaderboard</div>
          <p className="t-body-sm" style={{ maxWidth: "72ch", margin: 0 }}>
            Twenty proposal-only hypotheses ranked by frozen Prospect facts. Filters: stimulated DE at or above{" "}
            {fmt(campaign.method.min_stim_de)}, Rest DE at or below {fmt(campaign.method.max_rest_de)}, non-canonical,
            not housekeeping, on-target under stimulation, and cell-type-specific where measured.
          </p>
        </div>
        <a className="btn btn-secondary btn-sm" href="/data/agent_campaign.json" target="_blank" rel="noreferrer" style={{ marginLeft: "auto" }}>
          JSON <ExternalLink size={13} />
        </a>
      </div>
      <div className="card-paper" style={{ padding: 0, overflowX: "auto" }}>
        <table style={{ width: "100%", minWidth: 1120, borderCollapse: "collapse" }}>
          <thead>
            <tr className="t-label">
              {["rank", "gene", "lane", "status", "stim max", "Rest", "K562", "review", "risk"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: "9px 12px", borderBottom: "1px solid var(--rule)" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {campaign.candidates.slice(0, 12).map((r) => (
              <tr key={r.gene} style={{ borderTop: "1px solid var(--rule-faint)" }}>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px", color: "var(--ink-3)" }}>{r.rank}</td>
                <td style={{ padding: "8px 12px" }}>
                  <button onClick={() => onGene(r.gene)} className="t-mono" style={{ fontWeight: 700, background: "transparent", color: "var(--ink)" }}>{r.gene}</button>
                </td>
                <td style={{ padding: "8px 12px", maxWidth: 150 }}>
                  <span className="chip" style={{ ["--tone" as any]: "var(--field-blue)" }}>{r.priority_lane}</span>
                </td>
                <td style={{ padding: "8px 12px" }}>
                  <span className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>{r.status.replace(/_/g, " ")}</span>
                </td>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px", color: "var(--moss)", fontWeight: 650 }}>
                  {fmt(r.stim_max_de)} · {r.strongest_condition}
                </td>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px" }}>{fmt(r.rest_de)}</td>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px" }}>{r.k562_de == null ? "·" : fmt(r.k562_de)}</td>
                <td className="t-body-sm" style={{ padding: "8px 12px", maxWidth: 270, color: "var(--ink-2)" }}>{r.why_interesting}</td>
                <td className="t-body-sm" style={{ padding: "8px 12px", maxWidth: 250, color: "var(--ink-3)" }}>{r.what_would_weaken}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="t-caption" style={{ margin: 0 }}>
        Campaign <span className="t-mono">{campaign.campaign_id}</span> is {campaign.trust_boundary.replace(/_/g, " ")}.
        It ranks follow-ups; accepted state still requires the frozen gate and human key.
      </p>
    </div>
  );
}

function CampaignReviewAppendix({ review, onGene }: { review: CampaignReview; onGene: (g: string) => void }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Campaign review appendix</div>
          <p className="t-body-sm" style={{ maxWidth: "74ch", margin: 0 }}>
            A deterministic audit layer over the proposal-only campaign: what each row rests on, what would weaken it,
            and which candidates should advance to assay design first.
          </p>
        </div>
        <a className="btn btn-secondary btn-sm" href="/data/agent_campaign_review.json" target="_blank" rel="noreferrer" style={{ marginLeft: "auto" }}>
          JSON <ExternalLink size={13} />
        </a>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 8 }}>
        {Object.entries(review.lane_counts).map(([lane, count]) => (
          <div key={lane} style={{ padding: "9px 10px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
            <div className="t-mono" style={{ fontSize: 17, fontWeight: 700 }}>{count}</div>
            <div className="t-label" style={{ color: "var(--ink-3)", marginTop: 3 }}>{lane}</div>
          </div>
        ))}
      </div>
      <div className="card-paper" style={{ padding: 0, overflowX: "auto" }}>
        <table style={{ width: "100%", minWidth: 980, borderCollapse: "collapse" }}>
          <thead>
            <tr className="t-label">
              {["rank", "gene", "decision", "signal", "specificity", "stop rule"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: "9px 12px", borderBottom: "1px solid var(--rule)" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {review.rows.slice(0, 8).map((r) => (
              <tr key={r.gene} style={{ borderTop: "1px solid var(--rule-faint)" }}>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px", color: "var(--ink-3)" }}>{r.rank}</td>
                <td style={{ padding: "8px 12px" }}>
                  <button onClick={() => onGene(r.gene)} className="t-mono" style={{ fontWeight: 700, background: "transparent", color: "var(--ink)" }}>{r.gene}</button>
                </td>
                <td style={{ padding: "8px 12px" }}>
                  <span className="chip" style={{ ["--tone" as any]: r.decision === "advance_to_assay_design" ? "var(--brass)" : "var(--field-blue)" }}>
                    {r.decision.replace(/_/g, " ")}
                  </span>
                </td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--moss)", fontWeight: 650 }}>{r.stimulated_signal}</td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--ink-2)", maxWidth: 240 }}>{r.specificity}</td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--ink-3)", maxWidth: 300 }}>{r.stop_rules[0]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="t-caption" style={{ margin: 0 }}>
        Review <span className="t-mono">{review.campaign_id}</span> covers {review.candidate_count} proposal-only rows. It does not accept biological state.
      </p>
    </div>
  );
}

function CampaignAgentProbe({ probe, onGene }: { probe: CampaignAgentProbe; onGene: (g: string) => void }) {
  const tone = (alignment: string) => alignment === "aligned" ? "var(--moss)" :
    alignment === "more_aggressive" ? "var(--brass)" : alignment === "more_cautious" ? "var(--field-blue)" : "var(--stone)";
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Campaign agent probes</div>
          <p className="t-body-sm" style={{ maxWidth: "74ch", margin: 0 }}>
            Claude cross-examines the campaign rows with frozen lookup tools, then Prospect compares its
            recommendations to the deterministic review lane. The probe is proposal only.
          </p>
        </div>
        <a className="btn btn-secondary btn-sm" href="/data/campaign_agent_probe.json" target="_blank" rel="noreferrer" style={{ marginLeft: "auto" }}>
          JSON <ExternalLink size={13} />
        </a>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 8 }}>
        {Object.entries(probe.summary).map(([alignment, count]) => (
          <div key={alignment} style={{ padding: "9px 10px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
            <div className="t-mono" style={{ fontSize: 17, fontWeight: 700 }}>{count}</div>
            <div className="t-label" style={{ color: tone(alignment), marginTop: 3 }}>{alignment}</div>
          </div>
        ))}
      </div>
      <div className="card-paper" style={{ padding: 0, overflowX: "auto" }}>
        <table style={{ width: "100%", minWidth: 980, borderCollapse: "collapse" }}>
          <thead>
            <tr className="t-label">
              {["rank", "gene", "deterministic", "Claude probe", "alignment", "rationale"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: "9px 12px", borderBottom: "1px solid var(--rule)" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {probe.rows.map((r) => (
              <tr key={r.gene} style={{ borderTop: "1px solid var(--rule-faint)" }}>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px", color: "var(--ink-3)" }}>{r.rank}</td>
                <td style={{ padding: "8px 12px" }}>
                  <button onClick={() => onGene(r.gene)} className="t-mono" style={{ fontWeight: 700, background: "transparent", color: "var(--ink)" }}>{r.gene}</button>
                </td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--ink-2)" }}>{r.deterministic_decision.replace(/_/g, " ")}</td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--ink-2)" }}>{r.agent_recommendation.replace(/_/g, " ")}</td>
                <td style={{ padding: "8px 12px" }}>
                  <span className="chip" style={{ ["--tone" as any]: tone(r.alignment) }}>{r.alignment.replace(/_/g, " ")}</span>
                </td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--ink-3)", maxWidth: 340 }}>{r.agent_rationale}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="t-caption" style={{ margin: 0 }}>
        Probe <span className="t-mono">{probe.probe_id}</span> used {probe.tool_call_count} tool calls.
        No candidate enters accepted state from this artifact.
      </p>
    </div>
  );
}

function CampaignDisagreementTriage({ triage, onGene }: { triage: CampaignTriage; onGene: (g: string) => void }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Campaign disagreement triage</div>
          <p className="t-body-sm" style={{ maxWidth: "74ch", margin: 0 }}>
            When Claude pushes harder than the deterministic lane, Prospect turns the disagreement into
            assay gates, not accepted state. These rows stay proposal only.
          </p>
        </div>
        <a className="btn btn-secondary btn-sm" href="/data/campaign_triage.json" target="_blank" rel="noreferrer" style={{ marginLeft: "auto" }}>
          JSON <ExternalLink size={13} />
        </a>
      </div>
      <div className="card-paper" style={{ padding: 0, overflowX: "auto" }}>
        <table style={{ width: "100%", minWidth: 980, borderCollapse: "collapse" }}>
          <thead>
            <tr className="t-label">
              {["rank", "gene", "Claude probe", "Prospect triage", "signal", "assay gate"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: "9px 12px", borderBottom: "1px solid var(--rule)" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {triage.rows.map((r) => (
              <tr key={r.gene} style={{ borderTop: "1px solid var(--rule-faint)" }}>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px", color: "var(--ink-3)" }}>{r.rank}</td>
                <td style={{ padding: "8px 12px" }}>
                  <button onClick={() => onGene(r.gene)} className="t-mono" style={{ fontWeight: 700, background: "transparent", color: "var(--ink)" }}>{r.gene}</button>
                </td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--ink-2)" }}>{r.agent_recommendation.replace(/_/g, " ")}</td>
                <td style={{ padding: "8px 12px" }}>
                  <span className="chip" style={{ ["--tone" as any]: "var(--field-blue)" }}>{r.triage_decision.replace(/_/g, " ")}</span>
                </td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--moss)", fontWeight: 650 }}>{r.stimulated_signal}</td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--ink-3)", maxWidth: 360 }}>{r.assay_gate}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="t-caption" style={{ margin: 0 }}>
        Source probe <span className="t-mono">{triage.source_probe_id}</span>. Trust boundary: {triage.trust_boundary.replace(/_/g, " ")}.
      </p>
    </div>
  );
}

function LabPacketCard({ packet, onGene }: { packet: LabPacket; onGene: (g: string) => void }) {
  const rows = packet.candidates.slice(0, 5);
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Wet-lab assay packet</div>
          <p className="t-body-sm" style={{ maxWidth: "72ch", margin: 0 }}>
            Five proposal-only follow-ups translated into assay design: intervention, controls, readouts,
            exclusion rules, and public replay links. Status remains {packet.status.replace(/_/g, " ")}.
          </p>
        </div>
        <a className="btn btn-secondary btn-sm" href="/data/lab_packet.json" target="_blank" rel="noreferrer" style={{ marginLeft: "auto" }}>
          JSON <ExternalLink size={13} />
        </a>
      </div>
      <div className="card-paper" style={{ padding: 0, overflowX: "auto" }}>
        <table style={{ width: "100%", minWidth: 860, borderCollapse: "collapse" }}>
          <thead>
            <tr className="t-label">
              {["rank", "gene", "intervention", "primary readout", "controls", "exclude if"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: "9px 12px", borderBottom: "1px solid var(--rule)" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.gene} style={{ borderTop: "1px solid var(--rule-faint)" }}>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px", color: "var(--ink-3)" }}>{r.rank}</td>
                <td style={{ padding: "8px 12px" }}>
                  <button onClick={() => onGene(r.gene)} className="t-mono" style={{ fontWeight: 700, background: "transparent", color: "var(--ink)" }}>{r.gene}</button>
                </td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--ink-2)" }}>{r.intervention}</td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--ink-3)" }}>{r.primary_readout}</td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--ink-3)" }}>
                  {r.positive_controls.join(", ")} / {r.negative_controls[0]}
                </td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--ink-3)" }}>
                  {r.exclusion_criteria.slice(0, 2).join(", ")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="t-caption" style={{ margin: 0 }}>
        Replay: {packet.method.replay_links.map((link, i) => (
          <span key={link}>
            {i > 0 ? " · " : ""}
            <span className="t-mono">{link}</span>
          </span>
        ))}. Trust boundary: {packet.trust_boundary.replace(/_/g, " ")}.
      </p>
    </div>
  );
}

function PGGT1BDeepDiveCard({ dive, onGene }: { dive: PGGT1BDeepDive; onGene: (g: string) => void }) {
  const f = dive.facts;
  return (
    <div className="card-paper" style={{ padding: "16px 18px", display: "grid", gap: 12 }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <span className="t-label" style={{ color: "var(--brass)" }}>PGGT1B deep dive</span>
        <button onClick={() => onGene(dive.gene)} className="t-mono" style={{ fontSize: 16, fontWeight: 700, background: "transparent", color: "var(--ink)" }}>
          {dive.gene}
        </button>
        <span className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>{dive.status.replace(/_/g, " ")}</span>
        <a className="btn btn-secondary btn-sm" href="/data/pggt1b_deep_dive.json" target="_blank" rel="noreferrer" style={{ marginLeft: "auto" }}>
          JSON <ExternalLink size={13} />
        </a>
      </div>
      <p className="t-body-sm" style={{ maxWidth: "74ch", margin: 0 }}>
        {dive.prospect_read} External literature makes the prenylation mechanism plausible; it does not move accepted state.
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(128px, 1fr))", gap: 8 }}>
        {[
          ["Rest DE", fmt(f.rest_de), f.rest_kd],
          ["Stim8hr DE", fmt(f.stim8hr_de), f.stim8hr_kd],
          ["Stim48hr DE", fmt(f.stim48hr_de), f.stim48hr_kd],
          ["K562 DE", f.k562_de == null ? "not measured" : fmt(f.k562_de), "non-immune"],
          ["CollecTRI", fmt(f.collectri_targets), "targets"],
        ].map(([label, value, note]) => (
          <div key={label} style={{ padding: "9px 10px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
            <div className="t-label" style={{ color: "var(--ink-3)" }}>{label}</div>
            <div className="t-mono" style={{ fontSize: 16, fontWeight: 700, marginTop: 2 }}>{value}</div>
            <div className="t-caption" style={{ color: "var(--ink-3)", marginTop: 2 }}>{note}</div>
          </div>
        ))}
      </div>
      {dive.validation_plan && (
        <div style={{ display: "grid", gap: 8, paddingTop: 2 }}>
          <div className="t-label">Assay decision plan</div>
          <p className="t-body-sm" style={{ margin: 0, maxWidth: "80ch" }}>
            {dive.validation_plan.primary_readout}. {dive.validation_plan.expected_pattern}.
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 10 }}>
            <div>
              <div className="t-label" style={{ color: "var(--ink-3)", marginBottom: 4 }}>Controls</div>
              <p className="t-caption" style={{ margin: 0 }}>
                Negative: {dive.validation_plan.negative_controls.join(", ")}. Positive: {dive.validation_plan.positive_controls.join(", ")}.
              </p>
            </div>
            <div>
              <div className="t-label" style={{ color: "var(--ink-3)", marginBottom: 4 }}>Stop rules</div>
              <p className="t-caption" style={{ margin: 0 }}>{dive.validation_plan.stop_rules.slice(0, 2).join("; ")}.</p>
            </div>
          </div>
        </div>
      )}
      <div style={{ display: "grid", gap: 6 }}>
        <div className="t-label">Literature hooks</div>
        {dive.literature_context.map((ref) => (
          <a key={ref.doi} href={ref.url} target="_blank" rel="noreferrer" className="t-body-sm"
            style={{ color: "var(--field-blue)", textDecoration: "none" }}>
            {ref.year} {ref.journal}, DOI {ref.doi} <ExternalLink size={12} style={{ display: "inline", verticalAlign: -2 }} />
          </a>
        ))}
      </div>
      <p className="t-caption" style={{ margin: 0 }}>
        Assay: {dive.assay_readout}. Claim scope remains {dive.claim_scope.replace(/_/g, " ")}.
      </p>
    </div>
  );
}

function ValidationShortlist({ rows, onGene }: { rows: NonNullable<Data["validation"]>; onGene: (g: string) => void }) {
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div>
        <div className="t-label" style={{ marginBottom: 5 }}>Wet-lab validation shortlist</div>
        <p className="t-body-sm" style={{ maxWidth: "70ch", margin: 0 }}>
          Frozen lookups ranked into hypotheses to test: non-canonical, condition-specific, not housekeeping,
          inert in non-immune cells where measured, and no broad annotated regulon when possible.
        </p>
      </div>
      <div className="card-paper" style={{ padding: 0, overflowX: "auto" }}>
        <table style={{ width: "100%", minWidth: 720, borderCollapse: "collapse" }}>
          <thead>
            <tr className="t-label">
              {["gene", "status", "stim max", "Rest", "K562", "regulon", "assay-ready note"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: "9px 12px", borderBottom: "1px solid var(--rule)" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.gene} style={{ borderTop: "1px solid var(--rule-faint)" }}>
                <td style={{ padding: "8px 12px" }}>
                  <button onClick={() => onGene(r.gene)} className="t-mono" style={{ fontWeight: 700, background: "transparent", color: "var(--ink)" }}>{r.gene}</button>
                </td>
                <td style={{ padding: "8px 12px" }}><span className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>{r.status.replace(/_/g, " ")}</span></td>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px", color: "var(--moss)", fontWeight: 650 }}>{fmt(Number(r.stim_max_de))}</td>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px" }}>{fmt(Number(r.rest_de))}</td>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px" }}>{r.k562_de || "·"}</td>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px" }}>{r.known_regulon_targets}</td>
                <td className="t-body-sm" style={{ padding: "8px 12px", color: "var(--ink-3)" }}>
                  {r.strongest_condition} follow-up · targeted RNA-seq
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="t-caption" style={{ margin: 0 }}>
        Full sheet: <span className="t-mono">examples/data/validation_candidates.csv</span> and <span className="t-mono">docs/WETLAB_VALIDATION.md</span>.
      </p>
    </div>
  );
}

function Findings({ d, onGene }: { d: Data; onGene: (g: string) => void }) {
  const byKind = Object.fromEntries(d.findings.map((f) => [f.kind, f]));
  const order = ["activation_module", "regulator_vs_effector", "essentiality_artifact", "cross_cell_type_transfer", "regulon_recovery"];
  return (
    <div style={{ display: "grid", gap: 30 }}>
      <div>
        <h2 className="h1-display" style={{ marginBottom: 6 }}>Findings</h2>
        <p className="reading" style={{ maxWidth: "62ch", fontSize: "1rem" }}>
          Findings mined deterministically from the released table and signed into the frontier. The screen recovers
          known activation biology, catches the field’s most-targeted genes being mislabeled as regulators, resists the
          essentiality artifact a naive ranking surfaces, and confirms the split against a second cell type.
        </p>
      </div>
      {d.finding_index && <FindingsIndex index={d.finding_index} />}
      {order.map((k) => {
        const f = byKind[k] as Finding | undefined;
        if (!f) return null;
        return (
          <section key={k} style={{ display: "grid", gap: 12 }}>
            <FindingHead f={f} />
            {k === "activation_module" && <ActivationEvidence f={f} />}
            {k === "regulator_vs_effector" && <EffectorEvidence f={f} d={d} onGene={onGene} />}
            {k === "essentiality_artifact" && <EssentialityEvidence f={f} />}
            {k === "cross_cell_type_transfer" && <TransferEvidence f={f} onGene={onGene} />}
            {k === "regulon_recovery" && <RegulonEvidence f={f} onGene={onGene} />}
          </section>
        );
      })}
      {d.surprises.untested_famous?.length > 0 && (
        <section style={{ display: "grid", gap: 8 }}>
          <div className="t-label">Famous genes the screen could not test</div>
          <p className="t-body-sm" style={{ maxWidth: "66ch", margin: 0 }}>
            No effective knockdown, so the assay is silent on these, honest gaps, not evidence of absence.
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 2 }}>
            {d.surprises.untested_famous.map((x: any) => (
              <span key={x.gene} className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>{x.gene}</span>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function FindingsIndex({ index }: { index: FindingIndex }) {
  return (
    <section style={{ display: "grid", gap: 10, padding: "2px 0 8px" }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Scannable findings index</div>
          <p className="t-body-sm" style={{ maxWidth: "72ch", margin: 0 }}>
            Five reproduced finding objects, ordered for the demo: recover known biology, catch overclaiming,
            resist the housekeeping artifact, transfer the checker, then recover regulons.
          </p>
        </div>
        <a className="btn btn-secondary btn-sm" href="/data/finding_index.json" target="_blank" rel="noreferrer" style={{ marginLeft: "auto" }}>
          JSON <ExternalLink size={13} />
        </a>
      </div>
      <div style={{ display: "grid", gap: 0, borderTop: "1px solid var(--rule)", borderBottom: "1px solid var(--rule)" }}>
        {index.items.map((item) => (
          <div key={item.kind} style={{ display: "grid", gridTemplateColumns: "44px minmax(0, 1fr)", gap: 12,
            alignItems: "start", padding: "10px 0", borderTop: item.rank === 1 ? "none" : "1px solid var(--rule-faint)" }}>
            <span className="t-mono fz-sm" style={{ color: "var(--ink-3)" }}>F{item.rank}</span>
            <div style={{ display: "grid", gap: 4 }}>
              <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                <span className="t-body-sm" style={{ fontWeight: 700 }}>{item.title}</span>
                <span className="chip" style={{ ["--tone" as any]: item.challenge_status === "contradicted" ? "var(--cinnabar)" : "var(--moss)" }}>
                  {item.challenge_status === "contradicted" ? "contradiction surfaced" : item.status.replace(/_/g, " ")}
                </span>
                <span className="t-mono fz-sm" style={{ color: "var(--ink-3)" }}>{fmt(item.n_genes)} genes</span>
              </div>
              <p className="t-body-sm" style={{ margin: 0 }}>{item.readout}</p>
              <p className="t-caption" style={{ margin: 0, color: "var(--ink-3)" }}>{item.takeaway}</p>
            </div>
          </div>
        ))}
      </div>
      <p className="t-caption" style={{ margin: 0 }}>
        Source <span className="t-mono">{index.source}</span>. The index summarizes signed objects; evidence tables below carry the numbers.
      </p>
    </section>
  );
}

function EdgeChips({ items, keyName }: { items: Edge[]; keyName: "t" | "s" }) {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
      {items.map((x, i) => (
        <span key={i} title={`log2FC ${x.e}`} className="t-mono"
          style={{ fontSize: 11.5, padding: "2px 7px", borderRadius: 5, fontWeight: 600,
            background: x.d === "up" ? "var(--state-verified-tint)" : "var(--state-refuted-tint)",
            color: x.d === "up" ? "var(--moss)" : "var(--cinnabar)" }}>
          {(x as any)[keyName]}
        </span>
      ))}
    </div>
  );
}

function Peek({ node, d, onClose }: { node: Node; d: Data; onClose: () => void }) {
  const out = d.out[node.g] || [], inn = d.in[node.g] || [];
  const cons = d.contra.filter((x) => x.gene === node.g);
  const c = CLASS[node.cls];
  return (
    <>
      <div onClick={onClose} style={{ position: "fixed", inset: 0, background: "color-mix(in oklab, var(--ink) 22%, transparent)", zIndex: 49 }} />
      <div className="peek-panel" style={{ top: 0, width: "min(30rem, 94vw)", zIndex: 50 }}>
        <div className="peek-panel__inner">
          <button onClick={onClose} className="btn btn-ghost btn-sm" style={{ float: "right" }}>close</button>
          <div className="h1-display" style={{ fontFamily: "var(--font-mono)" }}>{node.g}</div>
          <div className="chip" style={{ ["--tone" as any]: c[0], marginTop: 6 }}>{c[1]}</div>
          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 16, fontSize: 12.5 }} className="t-num">
            <thead><tr className="t-label">{["condition", "status", "DE", "downstream", "effect"].map((h) => (
              <th key={h} style={{ textAlign: "left", padding: "6px 4px", borderBottom: "1px solid var(--rule)" }}>{h}</th>))}</tr></thead>
            <tbody>{CONDS.map((cd) => { const v = node.C[cd]; if (!v) return null; return (
              <tr key={cd} style={{ borderBottom: "1px solid var(--rule-faint)" }}>
                <td style={{ padding: "6px 4px" }}>{cd}</td>
                <td style={{ padding: "6px 4px", color: STA[v.s], fontWeight: 600 }}>{v.s.replace(/_/g, " ")}</td>
                <td style={{ padding: "6px 4px" }}>{v.de}</td><td style={{ padding: "6px 4px" }}>{fmt(v.dn)}</td>
                <td style={{ padding: "6px 4px" }}>{v.es}</td>
              </tr>); })}</tbody>
          </table>
          {out.length > 0 && (
            <div className="nb">
              <div className="nbh">Regulates {fmt(node.od)} genes <span className="mut">· knockdown changes these (top by effect · <span style={{ color: "var(--moss)" }}>up</span> / <span style={{ color: "var(--cinnabar)" }}>down</span>)</span></div>
              <EdgeChips items={out} keyName="t" />
            </div>
          )}
          {inn.length > 0 && (
            <div className="nb">
              <div className="nbh">Regulated by {fmt(node.id)} <span className="mut">· upstream genes whose knockdown moves {node.g}</span></div>
              <EdgeChips items={inn} keyName="s" />
            </div>
          )}
          {cons.length > 0 && (
            <div className="nb">
              <div className="nbh" style={{ color: "var(--cinnabar)" }}>Contradiction{cons.length > 1 ? "s" : ""} on record</div>
              {cons.slice(0, 4).map((x, i) => (
                <div key={i} className="t-body-sm" style={{ margin: "4px 0" }}>{x.claimant} claimed “{x.claim}” → data verdict <b>{x.verdict}</b></div>
              ))}
            </div>
          )}
          <p className="t-caption" style={{ marginTop: 16 }}>
            Edges sliced from the released Marson DE matrix (log2FC + adj. p). Re-derivable from frozen data; no model in the trust path.
          </p>
        </div>
      </div>
    </>
  );
}
