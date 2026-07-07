"use client";

import { useEffect, useMemo, useState } from "react";
import {
  LayoutGrid, Network, Waypoints, Sparkles, Search, ShieldCheck,
} from "lucide-react";
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent,
  SidebarHeader, SidebarInset, SidebarMenu, SidebarMenuButton, SidebarMenuItem,
  SidebarProvider, SidebarTrigger,
} from "@/components/ui/sidebar";
import { ThemeToggle } from "@/components/theme-toggle";

type Cond = { s: string; de: number; dn: number; es: number };
type Node = { g: string; cls: string; st: string; od: number; id: number; C: Record<string, Cond> };
type Edge = { t?: string; s?: string; d: string; e: number };
type Contra = { gene: string; claimant: string; claim: string; verdict: string; reason: string };
type Data = {
  stats: { n_genes: number; n_perturbations: number; dist: Record<string, number>; n_edges: number };
  atlas: Node[]; out: Record<string, Edge[]>; in: Record<string, Edge[]>;
  contra: Contra[]; open: string[];
  surprises: { hidden_regulators: any[]; demoted_famous: any[]; untested_famous: any[] };
  demo: { text: string; gene: string; status: string; reason: string }[];
  phantom: any; models: any[];
  frontier: { root: string; signer: string; n_nodes: number; n_edges: number; n_contra: number; n_open: number };
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
  { k: "atlas", label: "Atlas", icon: Network },
  { k: "frontier", label: "Frontier", icon: Waypoints },
  { k: "surprises", label: "Surprises", icon: Sparkles },
];

export default function Page() {
  const [d, setD] = useState<Data | null>(null);
  const [tab, setTab] = useState("overview");
  const [q, setQ] = useState("");
  const [gene, setGene] = useState<string | null>(null);
  useEffect(() => { fetch("/data/frontier.json").then((r) => r.json()).then(setD); }, []);
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
                  const count = d ? (n.k === "atlas" ? d.stats.n_edges : n.k === "frontier" ? d.frontier.n_contra : undefined) : undefined;
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
              {tab === "frontier" && <Frontier d={d} onGene={setGene} />}
              {tab === "surprises" && <Surprises d={d} />}
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
          <p className="t-body-sm" style={{ color: "var(--stone)", marginTop: 10, maxWidth: "70ch" }}>
            Of {fmt(p.checkable)} claims the screen could verify, {p.refuted} were wrong. The {p.untestable_no_kd} it
            couldn’t test are excluded, not counted against the model.
          </p>
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

      {d.models.length > 0 && (
        <div>
          <div className="t-label" style={{ marginBottom: 4 }}>Generation is cheap; trustworthy surprise is scarce</div>
          <p className="t-body-sm" style={{ marginBottom: 10, maxWidth: "66ch" }}>
            The same blind test across model tiers. The cost of generating the claims is trivial; the rate at
            which they fail the data barely moves. Verification is the bottleneck, not generation.
          </p>
          <div className="card-paper" style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", minWidth: 440, borderCollapse: "collapse" }}>
              <thead>
                <tr className="t-label">
                  {["model", "cost", "claims verifiable", "contradicted"].map((h) => (
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

function Surprises({ d }: { d: Data }) {
  const s = d.surprises;
  return (
    <div style={{ display: "grid", gap: 26 }}>
      <div>
        <h2 className="h1-display" style={{ marginBottom: 6 }}>Serendipity</h2>
        <p className="reading" style={{ maxWidth: "58ch", fontSize: "1rem" }}>
          Verified findings you would never reach scrolling a spreadsheet. Every one is gated against ground truth.
        </p>
      </div>
      <div>
        <div className="h2-app" style={{ marginBottom: 4 }}>Hidden regulators</div>
        <p className="t-body-sm" style={{ marginBottom: 12, maxWidth: "66ch" }}>
          Ask which genes run a T cell and you hear PD-1, IL-2, the TCR. The data says the heaviest regulators are
          transcription machinery and metabolism — like <b>BCAT2</b>, a branched-chain amino-acid enzyme.
        </p>
        <div className="card-grid">
          {s.hidden_regulators.slice(0, 12).map((h: any) => (
            <div key={h.gene} className="card-paper" style={{ padding: "12px 14px" }}>
              <div className="t-mono" style={{ fontSize: 15, fontWeight: 650 }}>{h.gene}</div>
              <div className="t-caption" style={{ marginTop: 2 }}>{fmt(h.max_downstream)} downstream · verified regulator</div>
            </div>
          ))}
        </div>
      </div>
      <div>
        <div className="h2-app" style={{ marginBottom: 4 }}>Famous genes the data demotes</div>
        <div className="card-paper" style={{ padding: "12px 15px", marginBottom: 12, background: "var(--state-open-tint)" }}>
          <p className="t-body-sm" style={{ margin: 0 }}>
            <b>Read carefully.</b> These famous genes show ~no transcriptional change when knocked down <i>in this screen</i>
            — a real, verified result, not a claim they don’t matter (checkpoints like PD-1 act by signaling, not transcription).
          </p>
        </div>
        <div className="card-grid">
          {s.demoted_famous.map((x: any) => {
            const cc = CONDS.map((c, k) => (x.conditions[c] ? `${CL[k]}:${x.conditions[c].n_de}DE` : "")).filter(Boolean).join("  ");
            return (
              <div key={x.gene} className="card-paper" style={{ padding: "12px 14px" }}>
                <div className="t-mono" style={{ fontSize: 15, fontWeight: 650 }}>{x.gene}</div>
                <div className="t-caption" style={{ marginTop: 2 }}>no transcriptional effect · {cc}</div>
              </div>
            );
          })}
        </div>
      </div>
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
