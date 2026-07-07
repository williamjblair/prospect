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
type Data = {
  stats: { n_genes: number; n_perturbations: number; dist: Record<string, number>; n_edges: number };
  atlas: Node[]; out: Record<string, Edge[]>; in: Record<string, Edge[]>;
  contra: Contra[]; open: string[];
  surprises: { hidden_regulators: any[]; demoted_famous: any[]; untested_famous: any[] };
  findings: Finding[]; citations: Record<string, Cite>;
  proposal?: { model: string; proposed: number; admitted: number; rejected: number; cost_usd: number;
    delta_id: string; items: { gene: string; verdict: string; rationale: string }[] } | null;
  agent?: { model: string; goal: string; rounds: number; tool_calls: number; cost_usd: number;
    delta_id: string; signer?: string; hypothesis?: { gene: string; hypothesis: string; evidence: string[]; why_novel: string } | null;
    transcript: { round: number; tool: string; input: any; result: any }[] } | null;
  demo: { text: string; gene: string; status: string; reason: string }[];
  phantom: any; models: any[];
  frontier: { root: string; signer: string; n_nodes: number; n_edges: number; n_contra: number; n_open: number; n_findings: number };
};

const CONDS = ["Rest", "Stim8hr", "Stim48hr"];
const CL = ["R", "8", "48"];
const CLASS: Record<string, [string, string]> = {
  constitutive_regulator: ["var(--moss)", "constitutive regulator"],
  condition_specific_regulator: ["var(--field-blue)", "condition-specific regulator"],
  verified_non_regulator: ["var(--stone)", "verified non-regulator"],
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
  const [tab, setTab] = useState("overview");
  const [q, setQ] = useState("");
  const [gene, setGene] = useState<string | null>(null);
  const [focus, setFocus] = useState<string>("");
  const { resolvedTheme } = useTheme();
  const dark = resolvedTheme === "dark";
  useEffect(() => {
    fetch("/data/frontier.json").then((r) => r.json()).then((x: Data) => {
      setD(x);
      const hub = [...x.atlas].sort((a, b) => b.od - a.od)[0];
      setFocus(x.out["VAV1"] ? "VAV1" : hub ? hub.g : "VAV1");
    });
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
                  const count = d ? (n.k === "atlas" ? d.stats.n_edges : n.k === "frontier" ? d.frontier.n_contra : n.k === "findings" ? d.frontier.n_findings : n.k === "agent" ? d.agent?.tool_calls : undefined) : undefined;
                  return (
                    <SidebarMenuItem key={n.k}>
                      <SidebarMenuButton isActive={tab === n.k} tooltip={n.label}
                        onClick={() => setTab(n.k)} className="h-8 fz-sm">
                        <Icon aria-hidden strokeWidth={1.75} />
                        <span className="min-w-0 flex-1 truncate">{n.label}</span>
                        {typeof count === "number" && (
                          <span className="t-mono fz-2xs" style={{ color: "var(--ink-3)" }}>{fmt(count)}</span>
                        )}
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
          {!d ? (
            <div className="t-label">Loading the frontier…</div>
          ) : (
            <>
              {tab === "overview" && <Overview d={d} />}
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

function Stat({ n, label, tone }: { n: number; label: string; tone?: string }) {
  return (
    <div className="card-paper" style={{ padding: "14px 16px" }}>
      <div className="stat-figure" style={{ color: tone || "var(--ink)" }}>{fmt(n)}</div>
      <div className="t-label" style={{ marginTop: 4 }}>{label}</div>
    </div>
  );
}

function Overview({ d }: { d: Data }) {
  const p = d.phantom, dist = d.stats.dist;
  const order = ["constitutive_regulator", "condition_specific_regulator", "verified_non_regulator", "unverifiable_no_kd"];
  const rate = p?.checkable ? Math.round((p.refuted / p.checkable) * 100) : null;
  return (
    <div style={{ display: "grid", gap: 26 }}>
      <header className="detail-hero" style={{ paddingBottom: 4 }}>
        <div className="t-label" style={{ marginBottom: 8 }}>Verified regulatory frontier · CD4⁺ T cells</div>
        <h1 className="t-display" style={{ maxWidth: "18ch" }}>What actually regulates a human T cell.</h1>
        <p className="reading" style={{ marginTop: 12, maxWidth: "58ch", fontSize: "1rem" }}>
          A linked, human-signed graph of gene regulation — every node and edge re-derived from the released
          CRISPRi Perturb-seq data, never from a model. AI can assert a claim about any gene in seconds; here
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
                And on the <b style={{ color: "var(--lantern)" }}>{p.effector_total} genes the field targets most</b> —
                checkpoints and cytokines like PD-1, TIM-3, IL-2 — models called them a major regulator{" "}
                <b style={{ color: "var(--lantern)" }}>{p.effector_overclaimed}</b> times.{" "}
                The data shows near-zero transcriptional change: they are effectors, not drivers (Finding 02).
              </p>
            </div>
          )}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: 12 }}>
        <Stat n={d.stats.n_genes} label="genes mapped" />
        <Stat n={d.stats.n_edges} label="verified regulatory edges" tone="var(--moss)" />
        <Stat n={(dist.constitutive_regulator || 0) + (dist.condition_specific_regulator || 0)} label="verified regulators" />
        <Stat n={d.frontier.n_contra} label="contradictions on record" tone="var(--cinnabar)" />
      </div>

      <div className="card-paper" style={{ padding: "16px 18px" }}>
        <div className="t-label" style={{ marginBottom: 10 }}>Verified regulatory state across the genome</div>
        <div style={{ display: "flex", height: 12, borderRadius: 6, overflow: "hidden" }}>
          {order.map((k) => <div key={k} style={{ flex: dist[k] || 0, background: CLASS[k][0] }} />)}
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 16, marginTop: 10 }}>
          {order.map((k) => (
            <span key={k} className="t-body-sm" style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
              <span style={{ width: 10, height: 10, borderRadius: 3, background: CLASS[k][0] }} />
              {CLASS[k][1]} · {fmt(dist[k] || 0)}
            </span>
          ))}
        </div>
      </div>

      <div>
        <div className="t-label" style={{ marginBottom: 8 }}>A claim from Claude Science, checked</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {d.demo.map((x, i) => (
            <span key={i} className="chip" title={x.reason} style={{ ["--tone" as any]: DEMOC[x.status] }}>
              {x.gene} — {x.status.replace(/_/g, " ")}
            </span>
          ))}
        </div>
      </div>

      {d.proposal && (
        <div>
          <div className="t-label" style={{ marginBottom: 4 }}>Claude proposes; the data decides; a human signs</div>
          <p className="t-body-sm" style={{ marginBottom: 10, maxWidth: "68ch" }}>
            The loop, closed. Claude ({d.proposal.model.replace("claude-", "").replace(/-/g, " ")}) proposed{" "}
            {d.proposal.proposed} candidate regulators. The frozen verifier admitted{" "}
            <b style={{ color: "var(--moss)" }}>{d.proposal.admitted}</b> and rejected{" "}
            <b style={{ color: "var(--cinnabar)" }}>{d.proposal.rejected}</b> — no model in the trust path.
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
            Signed delta <span className="t-mono" style={{ color: "var(--gold-ink)" }}>{d.proposal.delta_id}</span>{" "}
            · Claude is genuinely useful at proposing; the admission decision is frozen re-derivation plus a human key.
          </p>
        </div>
      )}

      {d.models.length > 0 && (
        <div>
          <div className="t-label" style={{ marginBottom: 4 }}>Generation is cheap; trustworthy surprise is scarce</div>
          <p className="t-body-sm" style={{ marginBottom: 10, maxWidth: "66ch" }}>
            The same blind test across model tiers. The cost of generating the claims is trivial; the rate at
            which they fail the data barely moves. Verification is the bottleneck, not generation.
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
                      {m.refuted_rate != null ? Math.round(m.refuted_rate * 100) + "%" : "—"}
                    </td>
                    <td style={{ padding: "9px 14px", color: "var(--cinnabar)" }}>
                      {m.effector_total ? `${m.effector_overclaimed}/${m.effector_total}` : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
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
        Search a gene. Each row shows its verified class and per-condition status (R rest · 8 8h · 48 48h stim).
        Open a gene for its regulatory neighborhood — what it regulates, and the claims the data refused.
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
        The neighborhood around <b>{focus}</b> — {out.length} genes it regulates, {inn.length} that regulate it, and the
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

function Frontier({ d, onGene }: { d: Data; onGene: (g: string) => void }) {
  return (
    <div style={{ display: "grid", gap: 24 }}>
      <div>
        <h2 className="h1-display" style={{ marginBottom: 6 }}>The frontier</h2>
        <p className="reading" style={{ maxWidth: "58ch", fontSize: "1rem" }}>
          The verified graph is accepted state — re-derived from frozen data and signed by a human. Contradictions
          and open questions are kept as first-class, citable terrain.
        </p>
      </div>
      <div style={{ display: "flex", gap: 26, flexWrap: "wrap", alignItems: "center" }}>
        <div><div className="stat-figure">{fmt(d.frontier.n_edges)}</div><div className="t-label">verified edges</div></div>
        <div><div className="stat-figure" style={{ color: "var(--cinnabar)" }}>{fmt(d.frontier.n_contra)}</div><div className="t-label">contradictions</div></div>
        <div><div className="stat-figure" style={{ color: "var(--brass)" }}>{fmt(d.frontier.n_open)}</div><div className="t-label">open questions</div></div>
        <div style={{ marginLeft: "auto", textAlign: "right" }} className="t-caption">
          signed <span className="t-mono" style={{ color: "var(--gold-ink)" }}>{d.frontier.root}</span><br />
          by {d.frontier.signer} · no model in the trust path
        </div>
      </div>
      <div>
        <div className="t-label" style={{ marginBottom: 8 }}>Contradictions — where AI claims meet the data</div>
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
        <div className="t-label" style={{ marginBottom: 6 }}>Open frontier — the screen couldn’t test these</div>
        <p className="t-body-sm" style={{ marginBottom: 10, maxWidth: "64ch" }}>
          Knockdown never succeeded, so the data is silent — honest gaps, and the demand surface for the next experiments.
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
  cross_cell_type_transfer: { n: "04", title: "Verifier transfer — a second cell type", tone: "var(--field-blue)" },
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
      <span className="t-mono fz-sm" style={{ textAlign: "right" }}>K562 {per[g].k562_de ?? "—"} DE</span>
    </div>
  );
  return (
    <div style={{ display: "grid", gap: 12 }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div className="card-paper" style={{ padding: "14px 16px" }}>
          <div className="stat-figure" style={{ color: "var(--brass)" }}>{med.essentiality_artifact ?? "—"}</div>
          <div className="t-label" style={{ marginTop: 4 }}>essentiality artifacts · median K562 DE</div>
          <div className="t-caption" style={{ marginTop: 6 }}>{essRate}% replicate — housekeeping, as predicted</div>
        </div>
        <div className="card-paper" style={{ padding: "14px 16px" }}>
          <div className="stat-figure" style={{ color: "var(--moss)" }}>{med.activation_module ?? "—"}</div>
          <div className="t-label" style={{ marginTop: 4 }}>activation module · median K562 DE</div>
          <div className="t-caption" style={{ marginTop: 6 }}>{actRate}% are K562-inert — T-cell-specific</div>
        </div>
      </div>
      <p className="t-body-sm" style={{ maxWidth: "72ch", margin: "2px 0" }}>
        The same major-regulator claim, run through <b>get_checker(&quot;marson&quot;)</b> and{" "}
        <b>get_checker(&quot;replogle&quot;)</b> — one verifier shape, two frozen datasets. Essentiality
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
            <span className="t-mono fz-sm" style={{ textAlign: "right" }}>{r.dir_agree != null ? Math.round(r.dir_agree * 100) + "%" : "—"}</span>
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
    if (tool === "cross_cell_type") return `K562 ${result.k562_de ?? "—"} DE → ${result.verdict}`;
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
          {a.tool_calls} verified tool calls over {a.rounds} rounds · ${a.cost_usd}
        </div>
      </div>

      {h && (
        <div className="card-paper" style={{ padding: "18px 20px", borderColor: "var(--moss)" }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 10, flexWrap: "wrap", marginBottom: 6 }}>
            <span className="t-label" style={{ color: "var(--moss)" }}>Signed hypothesis</span>
            <button onClick={() => onGene(h.gene)} className="t-mono" style={{ fontSize: 17, fontWeight: 700, background: "transparent", color: "var(--ink)" }}>{h.gene}</button>
          </div>
          <p className="t-lede" style={{ fontSize: "1.05rem", marginBottom: 10 }}>{h.hypothesis}</p>
          <div className="t-label" style={{ marginBottom: 6 }}>Verified evidence</div>
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

      <div>
        <div className="t-label" style={{ marginBottom: 8 }}>How it got there — every step a frozen-data tool call</div>
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
            No effective knockdown, so the assay is silent on these — honest gaps, not evidence of absence.
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
              <div className="nbh">Regulates {fmt(node.od)} genes <span className="mut">— knockdown changes these (top by effect · <span style={{ color: "var(--moss)" }}>up</span> / <span style={{ color: "var(--cinnabar)" }}>down</span>)</span></div>
              <EdgeChips items={out} keyName="t" />
            </div>
          )}
          {inn.length > 0 && (
            <div className="nb">
              <div className="nbh">Regulated by {fmt(node.id)} <span className="mut">— upstream genes whose knockdown moves {node.g}</span></div>
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
