"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  LayoutGrid, Waypoints, Telescope, Search, ShieldCheck, ExternalLink, Bot,
} from "lucide-react";
import { useTheme } from "next-themes";
import { ThemeToggle } from "@/components/theme-toggle";
import { GraphView } from "@/components/graph-view";

const LIVE_CLAIM_RAIL_TITLE = "Follow one claim";

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
  evidence_capsule?: {
    title: string;
    status: string;
    trust_boundary: string;
    decision: string;
    strongest_condition: string;
    primary_readout: string;
    stimulated_to_rest_ratio: number | null;
    stimulated_to_k562_ratio: number | null;
    effect_balance: Record<string, { up_genes: number; down_genes: number; total_de: number; up_fraction: number; down_fraction: number }>;
    evidence_ladder: { claim: string; status: string; evidence: string }[];
    assay_gates: string[];
    missing_for_acceptance: string[];
  };
  matrix_slice?: {
    title: string;
    source_gene: string;
    condition: string;
    status: string;
    trust_boundary: string;
    n_thresholded_transcripts: number;
    n_up: number;
    n_down: number;
    top_up: { gene: string; direction: string; log_fc: number; adj_p_value: number }[];
    top_down: { gene: string; direction: string; log_fc: number; adj_p_value: number }[];
  };
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
type DefendedEvidencePacket = {
  gene: string;
  status: string;
  accepted: boolean;
  defended_discovery_status: string;
  honest_ceiling: string;
  packet_id: string;
  orthogonal_public_dataset_count: number;
  frozen_external_context_count: number;
  scored_evidence: { source: string; status: string; summary: string }[];
  support_audit: { source: string; evidence_role: string; counts_for_full_bar: boolean; reason: string }[];
  bar_clearance: { rung: string; status: string; basis: string; count?: number }[];
  open_gates: { gate: string; reason: string }[];
  kill_attempts: { kill_id: string; result: string; basis: string }[];
  mechanism: string;
  novelty_assessment?: {
    status: string;
    downgraded_novelty: boolean;
    plain_language: string;
    kept_claim: string;
    citations: { pmid: string; role: string; title: string }[];
  };
  mechanism_dossier?: {
    data_shows: string[];
    inference: string[];
    partners: string[];
  };
  druggability?: {
    target_chembl_id: string;
    caveat: string;
    example_compounds: { molecule_chembl_id: string; standard_type: string; standard_value: string; standard_units: string }[];
  };
  sade_feldman_signature_summary?: {
    genes: number;
    typed_status_counts: Record<string, number>;
    coverage_report?: { after?: { not_assayed: number } };
  };
  wet_lab_protocol?: {
    system: string;
    minimum_donors: number;
    timepoints: string[];
    arms: { id: string; intervention: string }[];
    readouts: string[];
    decision_gates: { support: string; refute: string };
  };
  real_world_hook: string;
  falsifiable_experiment: {
    system: string;
    perturbation: string;
    controls: string[];
    readout: string;
    refutes_if: string;
  };
  reproduce_command: string;
};
type OverclaimCounterPacket = {
  phase: string;
  status: string;
  packet_id: string;
  reproduce_command: string;
  counts: {
    model_checkable_claims: number;
    model_contradicted_claims: number;
    phase1_frontier_genes: number;
    phase1_survivors: number;
    phase1_refused_total: number;
    phase2_without_external_screen_hit: number;
    phase2_schmidt_non_hits: number;
    phase2_schmidt_orthogonal_phenotypes: number;
    phase2_comparable_external_contradictions: number;
    flagship_hypotheses: number;
  };
  rungs: { rung: string; status: string; source: string; contradicted?: number; refused?: number; no_supporting_screen_hit?: number; supported_alternatives?: number }[];
  flagship_boundary: { gene: string; claim_kind: string; accepted_state: string; next_acceptance_step: string };
};
type ClaudeScienceAcceptanceDemo = {
  demo_id: string;
  producer: string;
  source_dataset: string;
  real_export: boolean;
  claim_under_test: string;
  claude_science: {
    artifact_status: string;
    internal_review_status: string;
    internal_review_findings: number;
    session_caveat: string;
    auc: Record<string, number>;
  };
  live_connector?: {
    capture_id: string;
    originating_claude_science_ui_call: boolean;
    reviewer_result: string;
    proposal_id: string;
    proposal_url: string;
    receipt_id: string;
    evidence_mode: string;
    consulted_substrate_count: number;
    accepted: boolean;
    next: string;
    incremental_cost_usd: number;
    api_cap_usd: number;
  };
  prospect: {
    verifier: string;
    trust_path: string;
    accepted: boolean;
    next: string;
    typed_status_counts: {
      genes: number;
      drivers: number;
      evidence_attached: number;
      passengers: number;
      associative_only: number;
      contradicted: number;
      not_assayed: number;
    };
    receipt_id: string;
    proposal_id: string;
    coverage_report?: {
      before: { not_assayed: number; genes: number };
      after: { not_assayed: number; genes: number };
      substrates?: Record<string, any>;
    };
    ceiling: string;
  };
  verdicts: {
    gene: string;
    signature_roles: string[];
    typed_status: AcceptanceStatus;
    condition: string;
    n_total_de_genes: number | null;
    ontarget_effect_category: string;
    de_rank: number | null;
    signature_diff_R_minus_NR: number | null;
    signature_padj: number | null;
    reason: string;
  }[];
  commands: { claude_science: string; generic: string; server: string };
};
type Data = {
  stats: { n_genes: number; n_perturbations: number; dist: Record<string, number>; n_edges: number };
  atlas: Node[]; out: Record<string, Edge[]>; in: Record<string, Edge[]>;
  contra: Contra[]; open: string[];
  surprises: { hidden_regulators: any[]; demoted_famous: any[]; untested_famous: any[] };
  finding_index?: FindingIndex | null;
  findings: Finding[]; citations: Record<string, Cite>;
  proposal?: { model: string; proposed: number; admitted: number; rejected: number; cost_usd: number;
    delta_id: string; items: { gene: string; verdict: string; rationale: string }[] } | null;
  agent?: { model: string; goal: string; rounds: number; tool_calls: number; cost_usd: number;
    delta_id: string; signer?: string; hypothesis?: { gene: string; hypothesis: string; evidence: string[]; why_novel: string } | null;
    transcript: { round: number; tool: string; input: any; result: any }[] } | null;
  receipts?: { id: string; status: string; replayability: string; kind: string; subject: string[];
    claim: string; accepted: boolean; producer: any; n_evidence: number; n_artifacts: number;
    verifier: string; replay: string; legacy_attestation?: boolean; covered_root?: string;
    attestor?: string; interpretation_qualified?: boolean }[];
  receipt_bridge?: {
    frontier_root: string; receipt_count: number; replay: string; mcp_command: string; exported_files: string[];
    protocol_path?: { step: number; method: string; action: string; result: string; accepted: boolean }[];
  };
  external_run_receipt_demo?: {
    command: string; producer: string; domain: string; lineage_id: string; claim: string; frontier_root: string;
    typed_status: string; engine_verdict: string; receipt_id: string; accepted: boolean; next: string;
    verifier_replay: string; human_acceptance_requires: string[];
  };
  pggt1b_deep_dive?: PGGT1BDeepDive | null;
  overclaim_counter?: OverclaimCounterPacket | null;
  claude_science_acceptance_demo?: ClaudeScienceAcceptanceDemo | null;
  pggt1b_defended_evidence?: DefendedEvidencePacket | null;
  gse278572_comparator?: any;
  gse271788_calibration?: any;
  gse271788_activation_specificity?: any;
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
type AcceptanceStatus = "evidence_attached" | "associative_only" | "contradicted" | "not_assayed";
type AcceptanceVerdict = {
  gene: string;
  typed_status: AcceptanceStatus;
  condition: string;
  n_total_de_genes: number | null;
  reason: string;
};
type AcceptanceResult = {
  proposal_id: string;
  proposal_url: string;
  accepted: false;
  next: "human_signature_required";
  prospect: {
    receipt_id: string;
    typed_status_counts: Record<AcceptanceStatus | "drivers" | "passengers" | "genes", number>;
    ceiling: string;
  };
  comparability: { status: string; reason: string };
  evidence_mode: "primary_only" | "all_frozen";
  consulted_substrates: { substrate_id: string; label: string; comparability: string }[];
  dataset_verdicts: {
    gene: string; substrate_id: string; typed_status: AcceptanceStatus;
    comparability: string; magnitude: number | null; reason: string;
  }[];
  verdicts: AcceptanceVerdict[];
  warnings: string[];
};
const PUBLIC_ACCEPTANCE_SERVICE_URL = (process.env.NEXT_PUBLIC_PROSPECT_ACCEPTANCE_URL || "").trim().replace(/\/+$/, "");
const ACCEPTANCE_EXAMPLE = `IL7R
CCR7
PD-1
ENSG00000121410
NOTGENE`;

const NAV = [
  { k: "overview", label: "Check", icon: LayoutGrid },
  { k: "findings", label: "Evidence", icon: Telescope },
  { k: "agent", label: "Lead", icon: Bot },
  { k: "frontier", label: "Receipts", icon: Waypoints },
];

export default function Page() {
  const [d, setD] = useState<Data | null>(null);
  const [err, setErr] = useState(false);
  const [tab, setTab] = useState("overview");
  const [q, setQ] = useState("");
  const [gene, setGene] = useState<string | null>(null);
  const [focus, setFocus] = useState<string>("");
  const [graphLoading, setGraphLoading] = useState(false);
  const { resolvedTheme } = useTheme();
  const dark = resolvedTheme === "dark";
  useEffect(() => {
    fetch("/data/check.json")
      .then((r) => { if (!r.ok) throw new Error(String(r.status)); return r.json(); })
      .then((x: Data) => setD(x))
      .catch(() => setErr(true));
  }, []);
  useEffect(() => {
    if (!d || (tab !== "atlas" && tab !== "network") || d.atlas.length || graphLoading) return;
    setGraphLoading(true);
    fetch("/data/frontier.json")
      .then((r) => { if (!r.ok) throw new Error(String(r.status)); return r.json(); })
      .then((x: Data) => {
        setD(x);
        const hub = [...x.atlas].sort((a, b) => b.od - a.od)[0];
        setFocus(x.out["VAV1"] ? "VAV1" : hub ? hub.g : "VAV1");
      })
      .catch(() => setErr(true))
      .finally(() => setGraphLoading(false));
  }, [d, graphLoading, tab]);
  const node = useMemo(() => (d && gene ? d.atlas.find((n) => n.g === gene) : null), [d, gene]);
  const label = NAV.find((n) => n.k === tab)?.label ?? (tab === "atlas" || tab === "network" ? "Explorer" : "");

  const goSearch = () => { setTab("atlas"); setTimeout(() => document.getElementById("gene-search")?.focus(), 60); };

  return (
    <div className="prospect-console">
      <header className="console-topbar" aria-label="Prospect workflow">
        <div className="console-brand">
          <span>
            <span className="console-brand-name">Prospect</span>
            <span className="console-brand-sub">Released data, not clinical truth.</span>
          </span>
        </div>
        <nav className="console-nav" aria-label="Main sections">
          {NAV.map((n) => {
            const Icon = n.icon;
            return (
              <button
                key={n.k}
                type="button"
                className="console-nav-item"
                data-active={tab === n.k ? "true" : "false"}
                aria-current={tab === n.k ? "page" : undefined}
                onClick={() => setTab(n.k)}
              >
                <Icon aria-hidden strokeWidth={1.75} />
                <span>{n.label}</span>
              </button>
            );
          })}
        </nav>
        <div className="console-actions">
          <button onClick={goSearch} className="btn btn-secondary btn-sm">
            <Search /> <span className="fz-xs">Search a gene</span>
          </button>
          <ThemeToggle />
        </div>
      </header>

      <main className="app-main console-main">
        <div className="console-context-strip">
          <span className="t-label">{label}</span>
          <span className="t-mono">root_a8b0dcdd4024e12f</span>
          <span className="t-caption">human_signature_required before acceptance</span>
          <span className="console-status" style={{ marginLeft: "auto" }}>accepted=false</span>
        </div>
          {err ? (
            <div style={{ display: "grid", gap: 8, maxWidth: "48ch", paddingTop: 40 }}>
              <div className="h2-app">The frozen evidence did not load.</div>
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
              {tab === "atlas" && (graphLoading || !d.atlas.length
                ? <div className="t-body-sm" aria-busy="true">Loading the frozen gene explorer...</div>
                : <Atlas d={d} q={q} setQ={setQ} onGene={setGene} />)}
              {tab === "network" && (graphLoading || !d.atlas.length
                ? <div className="t-body-sm" aria-busy="true">Loading the frozen graph...</div>
                : <NetworkView d={d} focus={focus} setFocus={setFocus} dark={dark} onGene={setGene} />)}
              {tab === "frontier" && <Frontier d={d} onGene={setGene} />}
              {tab === "findings" && <Findings d={d} onGene={setGene} />}
              {tab === "agent" && <AgentView d={d} onGene={setGene} />}
            </>
          )}
      </main>

      {node && d && <Peek node={node} d={d} onClose={() => setGene(null)} />}
    </div>
  );
}

function Reproduce({ children }: { children: ReactNode }) {
  return (
    <details className="reproduce">
      <summary>Reproduce</summary>
      <div className="t-caption" style={{ display: "grid", gap: 4, color: "var(--ink-4)" }}>{children}</div>
    </details>
  );
}

function Overview({ d, setTab }: { d: Data; setTab: (tab: string) => void }) {
  const p = d.phantom;
  const ratePct = p?.checkable ? ((p.refuted / p.checkable) * 100).toFixed(1) : null;
  return (
    <div className="overview-stack" style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr)", gap: 30 }}>
      <header className="detail-hero" style={{ paddingBottom: 4 }}>
        <div className="t-label" style={{ marginBottom: 8 }}>Check your AI biology claim · CD4+ T cells</div>
        <h1 className="t-display" style={{ maxWidth: "19ch" }}>Which gene predictions behave as causal drivers?</h1>
        <p className="reading" style={{ marginTop: 12, maxWidth: "58ch", fontSize: "1rem" }}>
          Reproducible is not verified. Prospect checks an AI-generated gene list against frozen perturbation data,
          separates candidate drivers from passengers, and keeps every result proposal-only until a human key accepts it.
        </p>
        {ratePct != null && (
          <p className="t-body-sm" style={{ marginTop: 14, maxWidth: "58ch", color: "var(--ink-3)" }}>
            In this frozen assay,{" "}
            <strong style={{ color: "var(--cinnabar)", fontWeight: 700 }}>{ratePct}%</strong>{" "}
            of confident AI major-regulator claims are contradicted by the measured data. No model sits in the trust path.{" "}
            <button
              type="button"
              onClick={() => setTab("findings")}
              style={{ color: "var(--field-blue)", fontWeight: 600, background: "none", border: "none", padding: 0, cursor: "pointer", textDecoration: "underline", font: "inherit" }}
            >
              See the reliability benchmark.
            </button>
          </p>
        )}
      </header>

      <ProspectAcceptanceWorkbench />

      {d.claude_science_acceptance_demo && (
        <ClaudeScienceAcceptancePanel demo={d.claude_science_acceptance_demo} setTab={setTab} />
      )}

    </div>
  );
}

function ClaudeScienceAcceptancePanel({ demo, setTab }: { demo: ClaudeScienceAcceptanceDemo; setTab: (tab: string) => void }) {
  const counts = demo.prospect.typed_status_counts;
  const examples = {
    supported: demo.verdicts.filter((v) => v.typed_status === "evidence_attached").slice(0, 3),
    contradicted: demo.verdicts.filter((v) => v.typed_status === "contradicted").slice(0, 3),
    passengers: demo.verdicts.filter((v) => v.typed_status === "associative_only").slice(0, 3),
    open: demo.verdicts.filter((v) => v.typed_status === "not_assayed").slice(0, 3),
  };
  return (
    <section className="card-paper" style={{ padding: "16px 18px", display: "grid", gap: 14 }}>
      <div>
        <div className="t-label" style={{ marginBottom: 5 }}>A real Claude Science export, gated</div>
        <h2 className="h2-app" style={{ margin: 0 }}>Prospect separates drivers from passengers.</h2>
        <p className="t-body-sm" style={{ margin: "7px 0 0", maxWidth: "62ch", color: "var(--ink-3)" }}>
          A real Claude Science export from {demo.source_dataset} passed its own review with no issues. Prospect checked its
          {" "}{counts.genes} genes against the frozen Marson table: {counts.drivers} drivers, {counts.passengers} passengers,
          {" "}{counts.contradicted} contradicted, {counts.not_assayed} not assayed. accepted={String(demo.prospect.accepted)}.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: 8 }}>
        <VerdictExample title="evidence_attached" tone="var(--moss)" rows={examples.supported} />
        <VerdictExample title="associative_only" tone="var(--stone)" rows={examples.passengers} />
        <VerdictExample title="contradicted" tone="var(--cinnabar)" rows={examples.contradicted} />
        <VerdictExample title="not_assayed" tone="var(--stone)" rows={examples.open} />
      </div>

      <PerturbationMatrix rows={demo.verdicts.slice(0, 12)} />

      <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", borderTop: "1px solid var(--rule-faint)", paddingTop: 10 }}>
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => setTab("frontier")}>Open audit trail</button>
        <Reproduce>
          <div><a href="/data/claude_science_acceptance_demo.json" style={{ color: "inherit" }}>/data/claude_science_acceptance_demo.json</a>{demo.live_connector ? <> · <a href={demo.live_connector.proposal_url} style={{ color: "inherit" }}>live proposal</a></> : null}</div>
          <div><span className="t-mono">{demo.commands.claude_science || CLAUDE_SCIENCE_CONNECTOR_COMMAND}</span></div>
          <div><span className="t-mono">{demo.commands.generic || GENERIC_CONNECTOR_COMMAND}</span></div>
        </Reproduce>
      </div>
    </section>
  );
}

function PerturbationMatrix({ rows }: { rows: ClaudeScienceAcceptanceDemo["verdicts"] }) {
  const conditions = ["Rest", "Stim8hr", "Stim48hr"];
  return (
    <div className="perturbation-matrix">
      <div className="perturbation-matrix__head">
        <span>gene</span>
        {conditions.map((condition) => <span key={condition}>{condition}</span>)}
        <span>typed status</span>
      </div>
      {rows.map((row) => (
        <div key={`${row.gene}-${row.typed_status}`} className="perturbation-matrix__row">
          <span className="t-mono">{row.gene}</span>
          {conditions.map((condition) => {
            const active = row.condition === condition;
            const silent = row.n_total_de_genes == null || row.n_total_de_genes <= 10;
            return (
              <span
                key={condition}
                className="perturbation-cell"
                data-active={active ? "true" : "false"}
                data-status={active ? row.typed_status : silent ? "not_assayed" : "associative_only"}
              >
                {active ? row.n_total_de_genes ?? "na" : "·"}
              </span>
            );
          })}
          <span className="chip" style={{ ["--tone" as any]: statusTone(row.typed_status) }}>{row.typed_status}</span>
        </div>
      ))}
    </div>
  );
}

function ProspectAcceptanceWorkbench() {
  const [text, setText] = useState(ACCEPTANCE_EXAMPLE);
  const [result, setResult] = useState<AcceptanceResult | null>(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [claimMode, setClaimMode] = useState<"associative_signature" | "explicit_driver_claim">("associative_signature");
  const [claimSource, setClaimSource] = useState("");
  const [phenotype, setPhenotype] = useState("activation_transcriptome");
  const [publishToLedger, setPublishToLedger] = useState(false);
  const [loading, setLoading] = useState(false);
  const [fromFallback, setFromFallback] = useState(false);

  const run = async () => {
    const localService = typeof window !== "undefined" && ["localhost", "127.0.0.1"].includes(window.location.hostname)
      ? "http://127.0.0.1:8130"
      : "";
    const service = PUBLIC_ACCEPTANCE_SERVICE_URL || localService;
    setLoading(true);
    // If the hosted service is unreachable or unset, degrade to the committed
    // frozen fixture (the identical verdict the service returns for the default
    // example) rather than a bare error. The demo never dead-ends, and the
    // note below is explicit that this is the canned example, not a live check.
    const loadFallback = async () => {
      try {
        const res = await fetch("/data/acceptance_fallback.json");
        if (!res.ok) throw new Error("fallback missing");
        setResult((await res.json()) as AcceptanceResult);
        setFromFallback(true);
        setError("");
        setCopied(false);
      } catch {
        setResult(null);
        setFromFallback(false);
        setError("The hosted acceptance service is unreachable.");
      }
    };
    if (!service) {
      await loadFallback();
      setLoading(false);
      return;
    }
    try {
      const response = await fetch(`${service}/submit`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          text,
          filename: "submission.txt",
          source_name: "public_web_submitter",
          substrate_id: "marson_cd4_activation",
          claim_mode: claimMode,
          claim_context: claimMode === "explicit_driver_claim" ? {
            cell_type: "primary human CD4+ T cells",
            condition: "strongest",
            phenotype,
            source: claimSource,
          } : {},
          evidence_mode: "all_frozen",
          publish_to_ledger: publishToLedger,
        }),
      });
      const next = await response.json();
      if (!response.ok || next.error) throw new Error(next.error || `submission failed (${response.status})`);
      setResult(next as AcceptanceResult);
      setFromFallback(false);
      setError("");
      setCopied(false);
    } catch {
      await loadFallback();
    } finally {
      setLoading(false);
    }
  };

  const shareUrl = result ? (result.proposal_url.startsWith("http")
    ? result.proposal_url
    : `${PUBLIC_ACCEPTANCE_SERVICE_URL}${result.proposal_url}`) : "";
  const serviceGuideUrl = PUBLIC_ACCEPTANCE_SERVICE_URL ? `${PUBLIC_ACCEPTANCE_SERVICE_URL}/guide` : "";
  const serviceLedgerUrl = PUBLIC_ACCEPTANCE_SERVICE_URL ? `${PUBLIC_ACCEPTANCE_SERVICE_URL}/ledger` : "";
  const counts = result?.prospect.typed_status_counts;

  return (
    <section className="card-paper" style={{ padding: "16px 18px", display: "grid", gap: 14 }}>
      <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between", gap: 14, flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Run your own claim through Prospect</div>
          <h2 className="h2-app" style={{ margin: 0 }}>Paste a signature, DE table, ranked markers, or gene list.</h2>
          <p className="t-body-sm" style={{ margin: "7px 0 0", color: "var(--ink-3)", maxWidth: "78ch" }}>
            The canonical service normalizes identifiers and returns a cryptographic receipt plus a persistent proposal page.
            A contradicted verdict is possible only when you submit an explicit causal claim with a comparable phenotype.
          </p>
        </div>
        <span className="chip" style={{ ["--tone" as any]: "var(--cinnabar)" }}>accepted=false</span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 280px), 1fr))", gap: 12 }}>
        <div style={{ display: "grid", gap: 8 }}>
          <div role="group" aria-label="Claim mode" style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <button type="button" className="btn btn-secondary btn-sm" data-active={claimMode === "associative_signature"}
              onClick={() => setClaimMode("associative_signature")}>Associative signature</button>
            <button type="button" className="btn btn-secondary btn-sm" data-active={claimMode === "explicit_driver_claim"}
              onClick={() => setClaimMode("explicit_driver_claim")}>Explicit causal claim</button>
          </div>
          {claimMode === "explicit_driver_claim" && (
            <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)", gap: 8 }}>
              <input className="t-mono fz-xs" value={claimSource} onChange={(event) => setClaimSource(event.target.value)}
                aria-label="Causal claim source" placeholder="Claim or citation source" />
              <select className="t-mono fz-xs" value={phenotype} onChange={(event) => setPhenotype(event.target.value)}
                aria-label="Claim phenotype">
                <option value="activation_transcriptome">Activation transcriptome</option>
                <option value="cytokine_production">Cytokine production</option>
                <option value="clinical_response">Clinical response</option>
              </select>
            </div>
          )}
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            aria-label="Paste gene list, signature JSON, ranked marker table, or DE CSV"
            spellCheck={false}
            style={{
              minHeight: 180,
              width: "100%",
              resize: "vertical",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-sm)",
              background: "var(--paper-recessed)",
              color: "var(--ink)",
              padding: "10px 11px",
              lineHeight: 1.45,
            }}
            className="t-mono fz-xs"
          />
          <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
            <button type="button" className="btn btn-secondary btn-sm" onClick={run} disabled={loading || (claimMode === "explicit_driver_claim" && !claimSource.trim())}>
              {loading ? "Submitting" : "Submit to Prospect"}
            </button>
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => setText(ACCEPTANCE_EXAMPLE)}>Load example</button>
            {error && <span className="t-caption" style={{ color: "var(--cinnabar)" }}>{error}</span>}
          </div>
          <label className="t-caption" style={{ display: "flex", gap: 8, alignItems: "center", color: "var(--ink-3)" }}>
            <input type="checkbox" checked={publishToLedger} onChange={(event) => setPublishToLedger(event.target.checked)} />
            Publish this proposal and self-declared producer name to the public ledger
          </label>
          <p className="t-caption" style={{ margin: 0, color: "var(--ink-3)" }}>
            Leave publication off for private testing. Published artifacts are visible to anyone with the ledger URL.
          </p>
        </div>

        <div style={{ border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", padding: "10px 11px", background: "var(--paper-recessed)", display: "grid", gap: 10, alignSelf: "start" }}>
          {result ? (
            <>
              {fromFallback && (
                <p className="t-caption" style={{ margin: 0, color: "var(--ink-3)" }}>
                  Hosted service unreachable. Showing the identical frozen verdict for the default example from a committed fixture. Run <span className="t-mono">./prospect serve-acceptance</span> locally to check your own input.
                </p>
              )}
              <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                <span className="t-mono" style={{ fontWeight: 700 }}>{result.prospect.receipt_id}</span>
                <span className="chip" style={{ ["--tone" as any]: "var(--cinnabar)" }}>accepted=false</span>
                <span className="chip" style={{ ["--tone" as any]: "var(--stone)" }}>{result.next}</span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(86px, 1fr))", gap: 8 }}>
                <AcceptanceCount label="drivers" value={counts?.drivers || 0} tone="var(--brass)" />
                <AcceptanceCount label="passengers" value={counts?.passengers || 0} tone="var(--stone)" />
                <AcceptanceCount label="contradicted" value={counts?.contradicted || 0} tone="var(--cinnabar)" />
                <AcceptanceCount label="not_assayed" value={counts?.not_assayed || 0} tone="var(--ink-3)" />
              </div>
              <div style={{ overflowX: "auto", borderTop: "1px solid var(--rule-faint)", paddingTop: 8 }}>
                <table style={{ width: "100%", minWidth: 520, borderCollapse: "collapse" }}>
                  <thead>
                    <tr className="t-label">
                      {["gene", "status", "condition", "DE", "reason"].map((h) => (
                        <th key={h} style={{ textAlign: "left", padding: "6px 7px", borderBottom: "1px solid var(--rule)" }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.verdicts.slice(0, 80).map((row) => (
                      <tr key={`${row.gene}-${row.typed_status}`} style={{ borderTop: "1px solid var(--rule-faint)" }}>
                        <td className="t-mono" style={{ padding: "6px 7px", fontWeight: 700 }}>{row.gene}</td>
                        <td style={{ padding: "6px 7px" }}><span className="chip" style={{ ["--tone" as any]: statusTone(row.typed_status) }}>{row.typed_status}</span></td>
                        <td className="t-caption" style={{ padding: "6px 7px", color: "var(--ink-3)" }}>{row.condition || "not assayed"}</td>
                        <td className="t-caption" style={{ padding: "6px 7px", color: "var(--ink-3)" }}>{row.n_total_de_genes ?? "na"}</td>
                        <td className="t-caption" style={{ padding: "6px 7px", color: "var(--ink-3)" }}>{row.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                <button type="button" className="btn btn-secondary btn-sm"
                  onClick={() => {
                    if (!shareUrl) return;
                    navigator.clipboard?.writeText(shareUrl);
                    setCopied(true);
                  }}>
                  <ExternalLink /> <span>{copied ? "Copied result link" : "Copy result link"}</span>
                </button>
                <a className="t-mono fz-2xs" href={shareUrl} target="_blank" rel="noreferrer"
                  style={{ color: "var(--field-blue)", overflowWrap: "anywhere" }}>{shareUrl}</a>
              </div>
              {result.warnings.length > 0 && (
                <p className="t-caption" style={{ margin: 0, color: "var(--ink-3)" }}>{result.warnings.slice(0, 3).join("; ")}</p>
              )}
              <p className="t-caption" style={{ margin: 0, color: "var(--ink-3)" }}>
                comparability={result.comparability.status}. {result.consulted_substrates.length} frozen substrates consulted, each with its own comparability. {result.prospect.ceiling}
              </p>
            </>
          ) : (
            <div style={{ display: "grid", gap: 8, alignContent: "start" }}>
              <div className="t-label">No local setup required</div>
              <p className="t-body-sm" style={{ margin: 0, color: "var(--ink-3)" }}>
                The same frozen rule is exposed by the hosted service and MCP tools. The browser contains no classifier or receipt hashing code.
              </p>
              {PUBLIC_ACCEPTANCE_SERVICE_URL && (
                <p className="t-body-sm" style={{ margin: 0, color: "var(--ink-3)" }}>
                  Hosted service: <a href={serviceGuideUrl} target="_blank" rel="noreferrer">guide</a>
                  {" "}and <a href={serviceLedgerUrl} target="_blank" rel="noreferrer">public ledger</a>.
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function AcceptanceCount({ label, value, tone }: { label: string; value: number; tone: string }) {
  return (
    <div style={{ borderTop: `2px solid ${tone}`, paddingTop: 6 }}>
      <div className="stat-figure" style={{ fontSize: "1.3rem", color: tone }}>{fmt(value)}</div>
      <div className="t-label">{label}</div>
    </div>
  );
}

function statusTone(status: AcceptanceStatus) {
  if (status === "evidence_attached") return "var(--brass)";
  if (status === "contradicted") return "var(--cinnabar)";
  if (status === "associative_only") return "var(--stone)";
  return "var(--ink-3)";
}

function VerdictExample({
  title,
  tone,
  rows,
}: {
  title: string;
  tone: string;
  rows: ClaudeScienceAcceptanceDemo["verdicts"];
}) {
  return (
    <div style={{ borderTop: `2px solid ${tone}`, paddingTop: 8, display: "grid", gap: 6 }}>
      <div className="t-label">{title.replace(/_/g, " ")}</div>
      {rows.map((row) => (
        <div key={row.gene} style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
          <span className="t-mono" style={{ fontWeight: 700, color: tone }}>{row.gene}</span>
          <span className="t-caption" style={{ color: "var(--ink-3)", textAlign: "right" }}>
            {row.n_total_de_genes == null ? "not in table" : `${row.n_total_de_genes} DE`}
          </span>
        </div>
      ))}
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
      <h2 className="h1-display" style={{ marginBottom: 4 }}>Genes</h2>
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
      <h2 className="h1-display" style={{ marginBottom: 6 }}>Causal graph</h2>
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
        <span><i className="graph-legend-dot graph-legend-dot-focus" />focus gene</span>
        <span><i className="graph-legend-dot graph-legend-dot-regulator" />regulator</span>
        <span><i className="graph-legend-dot graph-legend-dot-target" />target</span>
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
  orthogonal_phenotype: ["var(--field-blue)", "orthogonal phenotype"],
  claimed: ["var(--stone)", "claimed"],
};
const BOUNDARY = ["AI output", "Receipt", "Proposal", "Review", "Replay", "Human sign-off", "Shared record"];
const BRIDGE_METHOD_ORDER = [
  "prospect.receipt.schema",
  "prospect.receipt.validate",
  "prospect.receipt.submit",
  "prospect.receipt.submit_artifact",
];
const EXTERNAL_RUN_COMMAND = "python examples/openresearch_receipt_client.py --json";
const CLAUDE_SCIENCE_CONNECTOR_COMMAND = "python examples/claude_science_connector_client.py --json";
const GENERIC_CONNECTOR_COMMAND = "python examples/prospect_connector_client.py --case openresearch --json";

function Receipts({
  receipts,
  bridge,
  externalDemo,
}: {
  receipts: NonNullable<Data["receipts"]>;
  bridge?: Data["receipt_bridge"];
  externalDemo?: Data["external_run_receipt_demo"];
}) {
  // The executable boundary demo. Static facts about the receipt bridge, so it renders without any packet.
  const receipt_bridge_demo = {
    command: "python examples/receipt_bridge_client.py --json",
    json_command: "python examples/receipt_bridge_client.py --json",
    transport: "MCP stdio",
    tools: BRIDGE_METHOD_ORDER,
    accepted: false,
    next: "human_signature_required",
  };
  const boundaryCommand = receipt_bridge_demo.json_command;
  const boundaryNext = receipt_bridge_demo.next;
  return (
    <div style={{ display: "grid", gap: 12 }}>
      <div>
        <div className="t-label" style={{ marginBottom: 4 }}>How an AI claim becomes reviewable</div>
        <p className="t-body-sm" style={{ maxWidth: "70ch", margin: 0 }}>
          A model can assert anything in a second. A receipt records what was claimed, which frozen artifacts
          it stands on, which facts the replay confirms, and what a human would need before accepting it.
          Any producer can emit one; the same frozen gate decides.
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
                An external workbench can discover the schema, validate a receipt, and submit it as a proposal.
                The result stays accepted=false until a human key signs.
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
                <div className="t-mono fz-2xs" style={{ color: "var(--ink-4)"}}>{step.method}</div>
                <div className="t-body-sm" style={{ color: "var(--ink-3)" }}>
                  {step.result === "proposal_only" ? "submit returns proposal only" : step.action}
                </div>
              </div>
            ))}
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap",
            padding: "9px 10px", border: "1px solid var(--rule-faint)",
            borderRadius: "var(--radius-sm)", background: "var(--gold-tint, var(--state-open-tint))" }}>
            <span className="t-label" style={{ color: "var(--gold-ink)" }}>Try the boundary</span>
            <span className="t-mono fz-2xs" style={{ color: "var(--ink-4)"}}>{boundaryCommand}</span>
            <span className="t-caption" style={{ color: "var(--ink-3)" }}>
              expected accepted=false, next={boundaryNext}
            </span>
          </div>
        </div>
      )}
      {externalDemo && (
        <div className="card-paper" style={{ padding: "12px 14px", display: "grid", gap: 12 }}>
          <div style={{ display: "flex", gap: 12, alignItems: "start", flexWrap: "wrap" }}>
            <div style={{ minWidth: 240, flex: 1 }}>
              <div className="t-label">External producer example</div>
              <p className="t-body-sm" style={{ margin: "4px 0 0", color: "var(--ink-3)" }}>
                An external auto-research producer submits a biology-shaped Perturb-seq reproduction.
                The Marson checker re-derives the local facts, then Prospect still holds it as proposal only.
              </p>
            </div>
            <span className="chip" style={{ ["--tone" as any]: "var(--moss)" }}>
              {externalDemo.typed_status.replace(/_/g, " ")}
            </span>
            <span className="chip" style={{ ["--tone" as any]: "var(--cinnabar)" }}>
              accepted={String(externalDemo.accepted)}
            </span>
          </div>
          <div style={{ display: "grid", gap: 6 }}>
            <div className="t-body-sm" style={{ fontWeight: 650 }}>{externalDemo.claim}</div>
            <div className="t-caption" style={{ color: "var(--ink-3)" }}>
              lineage <span className="t-mono">{externalDemo.lineage_id}</span> · receipt{" "}
              <span className="t-mono">{externalDemo.receipt_id}</span>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: 8 }}>
            <div style={{ padding: "8px 9px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)",
              background: "var(--paper-recessed)" }}>
              <div className="t-label">frozen replay</div>
              <div className="t-mono fz-2xs" style={{ color: "var(--ink-4)"}}>{externalDemo.verifier_replay}</div>
            </div>
            <div style={{ padding: "8px 9px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)",
              background: "var(--paper-recessed)" }}>
              <div className="t-label">bridge result</div>
              <div className="t-mono fz-2xs" style={{ color: "var(--ink-4)"}}>
                accepted=false · next={externalDemo.next}
              </div>
            </div>
            <div style={{ padding: "8px 9px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)",
              background: "var(--paper-recessed)" }}>
              <div className="t-label">judge command</div>
              <div className="t-mono fz-2xs" style={{ color: "var(--ink-4)"}}>
                {externalDemo.command || EXTERNAL_RUN_COMMAND}
              </div>
            </div>
          </div>
          <div>
            <div className="t-label" style={{ marginBottom: 5 }}>Human-only acceptance requires</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {externalDemo.human_acceptance_requires.map((item) => (
                <span key={item} className="chip" style={{ ["--tone" as any]: "var(--stone)" }}>
                  {item.replace(/_/g, " ")}
                </span>
              ))}
            </div>
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
                  <span className="t-caption" style={{ color: "var(--ink-3)" }}>
                    · {r.producer?.kind === "autonomous_agent" ? `agent (${r.n_evidence} reproduced facts)` : `${r.n_evidence} atoms · ${r.n_artifacts} artifacts`}
                    {r.legacy_attestation ? ` · legacy root attestation ${r.covered_root}` : ""}
                    {r.interpretation_qualified ? " · current interpretation qualified" : ""}
                  </span>
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
        re-derives from frozen data is <b>reproduced</b>; where a comparable causal claim disagrees it is <b>contradicted</b>.
        Legacy root attestations are provenance, not receipt acceptance. Every Receipt v1 row above remains accepted=false.
      </p>
    </div>
  );
}

function Frontier({ d, onGene }: { d: Data; onGene: (g: string) => void }) {
  return (
    <div className="frontier-pane" style={{ display: "grid", gap: 24 }}>
      <div>
        <h2 className="h1-display" style={{ marginBottom: 6 }}>Receipts</h2>
        <p className="reading" style={{ maxWidth: "56ch", fontSize: "1rem" }}>
          The audit trail behind the result. A model can assert anything; an accepted record needs a frozen replay and a human key.
        </p>
      </div>
      <div style={{ display: "flex", gap: 26, flexWrap: "wrap", alignItems: "center" }}>
        <div><div className="stat-figure">{fmt(d.frontier.n_edges)}</div><div className="t-label">reproduced edges</div></div>
        <div><div className="stat-figure" style={{ color: "var(--cinnabar)" }}>{fmt(d.frontier.n_contra)}</div><div className="t-label">contradictions</div></div>
        <div><div className="stat-figure">{fmt(d.frontier.n_open)}</div><div className="t-label">open questions</div></div>
        <div style={{ marginLeft: "auto", textAlign: "right" }} className="t-caption">
          root <span className="t-mono">{d.frontier.root}</span><br />
          by {d.frontier.signer} · no model in the trust path
        </div>
      </div>

      {d.receipts && d.receipts.length > 0 && (
        <details className="reproduce">
          <summary>How a claim becomes a receipt, and an external-producer example</summary>
          <div style={{ marginTop: 12 }}>
            <Receipts receipts={d.receipts} bridge={d.receipt_bridge} externalDemo={d.external_run_receipt_demo} />
          </div>
        </details>
      )}

      <div>
        <div className="t-label" style={{ marginBottom: 8 }}>Contradictions, where AI claims meet the data</div>
        <div className="card-paper" style={{ padding: 0, overflow: "hidden" }}>
          {d.contra.slice(0, 60).map((x, i) => (
            <button key={i} onClick={() => onGene(x.gene)} className="state-row"
              style={{ display: "flex", alignItems: "center", gap: 10, width: "100%", textAlign: "left",
                padding: "8px 14px", borderTop: i ? "1px solid var(--rule-faint)" : "none", background: "transparent",
                ["--state" as any]: "var(--cinnabar)" } as any}>
              <span className="t-mono" style={{ width: 84, flexShrink: 0, fontWeight: 650 }}>{x.gene}</span>
              <span className="chip" style={{ ["--tone" as any]: "var(--cinnabar)", flexShrink: 0 }}>{x.verdict}</span>
              <span className="t-body-sm" style={{ flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", color: "var(--ink-2)" }}>
                {x.claimant}: “{x.claim}”
              </span>
            </button>
          ))}
        </div>
      </div>
      <div>
        <div className="t-label" style={{ marginBottom: 6 }}>Not assayed, the screen could not test these</div>
        <p className="t-body-sm" style={{ marginBottom: 10, maxWidth: "64ch" }}>
          Knockdown never succeeded, so the data is silent, honest gaps, and the demand surface for the next experiments.
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
          {d.open.map((g) => <span key={g} className="chip" style={{ ["--tone" as any]: "var(--stone)" }}>{g}</span>)}
        </div>
      </div>
    </div>
  );
}

const FINDING_META: Record<string, { n: string; title: string; tone: string }> = {
  activation_module: { n: "01", title: "The activation module, rebuilt from perturbation", tone: "var(--moss)" },
  regulator_vs_effector: { n: "02", title: "Driver claim versus assay response", tone: "var(--moss)" },
  essentiality_artifact: { n: "03", title: "Rest reach is not activation specificity", tone: "var(--moss)" },
  cross_cell_type_transfer: { n: "04", title: "Cross-cell-context comparison", tone: "var(--moss)" },
  regulon_recovery: { n: "05", title: "Regulon recovery and sign disagreements", tone: "var(--moss)" },
};

const FINDING_PUBLIC_CLAIM: Record<string, string> = {
  regulator_vs_effector:
    "Eighteen field-targeted genes have effective knockdown but near-zero stimulated transcriptome reach in this assay. That result limits a broad causal-driver claim for this readout; it does not make the genes biologically irrelevant.",
  essentiality_artifact:
    "High Rest reach argues against activation specificity, but does not by itself establish housekeeping or essentiality. The independently frozen GSE278572 proposal qualifies MED12 under this exact rule.",
  cross_cell_type_transfer:
    "K562 and covered RPE1 rows test whether effects extend beyond primary CD4+ cells. Cross-cell reach is orthogonal evidence, not proof of housekeeping, and noncoverage is not a refutation.",
  regulon_recovery:
    "Known CollecTRI targets are enriched among moved genes. Sign disagreements identify context-sensitive edges for review; they do not by themselves overturn the literature.",
};

function FindingHead({ f }: { f: Finding }) {
  const m = FINDING_META[f.kind];
  const publicClaim = FINDING_PUBLIC_CLAIM[f.kind] ?? f.claim;
  return (
    <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 8 }}>
      <span className="t-mono" style={{ fontSize: 13, color: m.tone, fontWeight: 700 }}>{m.n}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <span className="h2-app">{m.title}</span>
          <span className="chip" style={{ ["--tone" as any]: m.tone }}>computationally_reproduced</span>
          {f.kind === "essentiality_artifact" && (
            <span className="chip" style={{ ["--tone" as any]: "var(--stone)" }}>evidence_attached qualification</span>
          )}
          <span className="t-mono fz-2xs" style={{ color: "var(--ink-4)" }}>{f.n_genes} genes · {f.cid}</span>
        </div>
        <p className="t-body-sm" style={{ marginTop: 6, maxWidth: "70ch" }}>{publicClaim}</p>
      </div>
    </div>
  );
}

function FindingEvidencePanel({ children }: { children: ReactNode }) {
  return (
    <div className="card-paper finding-evidence-panel">
      {children}
    </div>
  );
}

function FindingEvidenceRow({ cells, head }: { cells: ReactNode[]; head?: boolean }) {
  return (
    <div className={`finding-evidence-row${head ? " finding-evidence-row-head" : ""}`}>
      {cells.map((c, i) => (
        <span key={i} className={head ? "t-label" : i === 0 ? "t-mono" : "t-body-sm"}
          style={{ fontWeight: !head && i === 0 ? 650 : undefined }}>{c}</span>
      ))}
    </div>
  );
}

function EvRow({ cells, head }: { cells: ReactNode[]; head?: boolean }) {
  return <FindingEvidenceRow cells={cells} head={head} />;
}

function ActivationEvidence({ f }: { f: Finding }) {
  const ex: Record<string, { rest_de: number; stim_max_de: number }> = f.evidence.canonical_exemplar || {};
  const rows = Object.entries(ex).sort((a, b) => b[1].stim_max_de - a[1].stim_max_de).slice(0, 12);
  return (
    <FindingEvidencePanel>
      <EvRow head cells={["gene", "TCR-cascade component", "Rest → Stim (max) DE"]} />
      {rows.map(([g, v]) => (
        <EvRow key={g} cells={[g, "silent at rest, fires on stimulation",
          <span key="n"><b style={{ color: "var(--ink-4)" }}>{v.rest_de}</b> → <b style={{ color: "var(--moss)" }}>{fmt(v.stim_max_de)}</b></span>]} />
      ))}
    </FindingEvidencePanel>
  );
}

function EffectorEvidence({ f, d, onGene }: { f: Finding; d: Data; onGene: (g: string) => void }) {
  const per: Record<string, { stim_condition: string; n_de: number }> = f.evidence.per_gene || {};
  // Cited genes provide field context. The citation does not automatically assert this assay's causal readout.
  const cited = Object.keys(per).filter((g) => d.citations[g]).sort();
  const rest = Object.keys(per).filter((g) => !d.citations[g]).sort();
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <FindingEvidencePanel>
        <EvRow head cells={["gene", "published role (cited)", "DE on KD"]} />
        {cited.map((g) => {
          const c = d.citations[g], p = per[g];
          return (
            <div key={g} className="finding-evidence-row">
              <button onClick={() => onGene(g)} className="t-mono" style={{ fontWeight: 650, textAlign: "left",
                background: "transparent", color: "var(--field-blue)" }}>{g}</button>
              <span className="t-body-sm" style={{ minWidth: 0 }}>
                {c.canonical_role.split(":")[0]} ·{" "}
                <a href={`https://doi.org/${c.doi}`} target="_blank" rel="noreferrer"
                  className="t-caption" style={{ color: "var(--ink-3)", textDecoration: "none" }}>
                  {c.first_author} {c.year} <ExternalLink size={10} style={{ display: "inline", verticalAlign: "baseline" }} />
                </a>
              </span>
              <span className="t-mono fz-sm" style={{ textAlign: "right", fontWeight: 650, color: "var(--ink-3)"}}>
                {p.n_de} <span className="t-caption">({p.stim_condition})</span>
              </span>
            </div>
          );
        })}
      </FindingEvidencePanel>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, alignItems: "center" }}>
        <span className="t-caption">other low-effect targets:</span>
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
      <FindingEvidencePanel>
        <EvRow head cells={["gene", "high Rest reach in this assay", "Rest DE"]} />
        {rows.map(([g, v]) => (
          <EvRow key={g} cells={[g, "moves the transcriptome in a resting cell",
            <b key="n" style={{ color: "var(--brass)" }}>{fmt(v.rest_de)}</b>]} />
        ))}
      </FindingEvidencePanel>
      <div className="card-paper" style={{ padding: "10px 15px", background: "var(--state-open-tint)" }}>
        <p className="t-body-sm" style={{ margin: 0 }}>
          The frozen threshold separates a high-Rest group at DE ≥ <b>{fmt(gap.machinery_rest_de_min ?? 0)}</b> from
          the activation module, which tops out at Rest DE <b>{gap.activation_module_rest_de_max ?? 0}</b>. This is a
          descriptive specificity screen, not a housekeeping classifier. GSE278572 supplies the proposal-only MED12 qualification.
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
  // Recognizable exemplars: strongest cross-cell effects plus iconic TCR genes with low K562 reach.
  const broad = (e.housekeeping_exemplar || []).slice(0, 4);
  const immune = (e.immune_exemplar || []).slice(0, 4);
  const Row = ({ g, tone }: { g: string; tone: string }) => (
    <div className="finding-evidence-row">
      <button onClick={() => onGene(g)} className="t-mono" style={{ fontWeight: 650, textAlign: "left", background: "transparent", color: tone }}>{g}</button>
      <span className="t-body-sm">{per[g].finding === "essentiality_artifact" ? "high-Rest group · broad in K562" : "activation module · low K562 reach"}</span>
      <span className="t-mono fz-sm" style={{ textAlign: "right" }}>K562 {per[g].k562_de ?? "·"} DE</span>
    </div>
  );
  return (
    <div style={{ display: "grid", gap: 12 }}>
      <div className="finding-metric-strip">
        <div className="card-paper" style={{ padding: "14px 16px" }}>
          <div className="stat-figure">{med.essentiality_artifact ?? "·"}</div>
          <div className="t-label" style={{ marginTop: 4 }}>high-Rest group · median K562 DE</div>
          <div className="t-caption" style={{ marginTop: 6 }}>{essRate}% have broad K562 reach among covered genes</div>
        </div>
        <div className="card-paper" style={{ padding: "14px 16px" }}>
          <div className="stat-figure" style={{ color: "var(--moss)" }}>{med.activation_module ?? "·"}</div>
          <div className="t-label" style={{ marginTop: 4 }}>activation module · median K562 DE</div>
          <div className="t-caption" style={{ marginTop: 6 }}>{actRate}% have low or unavailable K562 reach</div>
        </div>
      </div>
      <p className="t-body-sm" style={{ maxWidth: "72ch", margin: "2px 0" }}>
        The same major-regulator claim, run through <b>get_checker(&quot;marson&quot;)</b> and{" "}
        <b>get_checker(&quot;replogle&quot;)</b>, one verifier shape, two frozen datasets. The high-Rest group has
        median K562 reach {med.essentiality_artifact} DE; the activation module has median {med.activation_module}.
        This qualifies cell-context breadth. It does not establish housekeeping, essentiality, or irrelevance to immune biology.
      </p>
      <FindingEvidencePanel>
        {broad.map((g: string) => <Row key={g} g={g} tone="var(--brass)" />)}
        {immune.map((g: string) => <Row key={g} g={g} tone="var(--moss)" />)}
      </FindingEvidencePanel>
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
      <div className="finding-metric-strip">
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
          <div className="t-label" style={{ marginTop: 4 }}>sign-disagreement edges</div>
          <div className="t-caption" style={{ marginTop: 6 }}>context-sensitive review candidates</div>
        </div>
      </div>
      <p className="t-body-sm" style={{ maxWidth: "72ch", margin: "2px 0" }}>
        Each TF's CollecTRI literature regulon, checked against the genes its knockdown actually moved,
        over the {e.n_tfs_tested} TFs that are major regulators here. {e.n_recovered} clear significance
        on their own, including the Th1 and Th2 master factors TBX21 and GATA3. Prospect re-derives
        regulon enrichment from perturbation alone, with no regulon supplied to the screen.
      </p>
      <FindingEvidencePanel>
        <div className="finding-evidence-row finding-evidence-row-head finding-evidence-row-four">
          {["TF", "known regulon recovered", "enrichment", "sign"].map((h, i) => (
            <span key={h} className="t-label" style={{ color: "var(--ink-3)", textAlign: i > 1 ? "right" : "left" }}>{h}</span>
          ))}
        </div>
        {top.map((r) => (
          <div key={r.tf} className="finding-evidence-row finding-evidence-row-four">
            <button onClick={() => onGene(r.tf)} className="t-mono" style={{ fontWeight: 650, textAlign: "left", background: "transparent", color: "var(--moss)" }}>{r.tf}</button>
            <span className="t-body-sm">{r.overlap} of {r.known} known targets moved on knockdown</span>
            <span className="t-mono fz-sm" style={{ textAlign: "right", color: "var(--moss)" }}>{r.fold}×</span>
            <span className="t-mono fz-sm" style={{ textAlign: "right" }}>{r.dir_agree != null ? Math.round(r.dir_agree * 100) + "%" : "·"}</span>
          </div>
        ))}
      </FindingEvidencePanel>
      {wrong.length > 0 && (
        <div>
          <div className="t-label" style={{ marginBottom: 6 }}>Where the assay sign disagrees with CollecTRI</div>
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
        <div className="t-label" style={{ marginBottom: 6 }}>Autonomous agent · Claude Opus 4.8</div>
        <h2 className="h1-display" style={{ marginBottom: 6 }}>The Claude Opus agent&apos;s one lead.</h2>
        <p className="reading" style={{ maxWidth: "60ch", fontSize: "1rem" }}>
          A Claude Opus agent searched for an under-appreciated CD4+ regulator over {a.tool_calls} frozen-data
          tool calls. Every fact below is a deterministic lookup; no model is in the trust path.
        </p>
      </div>

      {h && (
        <div className="card-paper" style={{ padding: "18px 20px" }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 10, flexWrap: "wrap", marginBottom: 8 }}>
            <span className="t-label" style={{ color: "var(--moss)" }}>Proposal worth testing</span>
            <button onClick={() => onGene(h.gene)} className="t-mono" style={{ fontSize: 17, fontWeight: 700, background: "transparent", color: "var(--ink)" }}>{h.gene}</button>
            <span className="chip" style={{ ["--tone" as any]: "var(--cinnabar)", marginLeft: "auto" }}>accepted=false</span>
          </div>
          <p className="t-lede" style={{ fontSize: "1.05rem", marginBottom: 12 }}>{h.hypothesis}</p>
          <ul style={{ margin: 0, paddingLeft: 0, listStyle: "none", display: "grid", gap: 5 }}>
            {h.evidence.map((e, i) => (
              <li key={i} className="t-body-sm" style={{ display: "flex", gap: 8 }}>
                <ShieldCheck size={14} style={{ color: "var(--moss)", flexShrink: 0, marginTop: 3 }} /> {e}
              </li>
            ))}
          </ul>
          <Reproduce>
            <div><a href="/data/pggt1b_defended_evidence.json" style={{ color: "inherit" }}>/data/pggt1b_defended_evidence.json</a> · <span className="t-mono">./prospect pggt1b-defended-evidence</span></div>
            <div>Goal: {a.goal}. Proposal {a.delta_id}{a.signer ? `, signed by ${a.signer}` : ""}, {a.rounds} rounds, ${a.cost_usd}. Why novel: {h.why_novel}</div>
          </Reproduce>
        </div>
      )}

      {d.pggt1b_deep_dive && (
        <details className="reproduce">
          <summary>PGGT1B, in detail</summary>
          <div style={{ marginTop: 12 }}>
            <PGGT1BDeepDiveCard dive={d.pggt1b_deep_dive} onGene={onGene} />
          </div>
        </details>
      )}

      <details className="reproduce">
        <summary>Search trail, {a.tool_calls} frozen-data tool calls</summary>
        <div className="card-paper" style={{ padding: 0, overflow: "hidden", marginTop: 12 }}>
          {a.transcript.map((t, i) => (
            <div key={i} style={{ display: "grid", gridTemplateColumns: "40px 1fr", gap: 10, alignItems: "center",
              padding: "7px 14px", borderTop: i ? "1px solid var(--rule-faint)" : "none" }}>
              <span className="t-mono fz-2xs" style={{ color: "var(--ink-4)" }}>r{t.round}</span>
              <div style={{ display: "flex", gap: 8, alignItems: "baseline", flexWrap: "wrap", minWidth: 0 }}>
                <span className="t-mono fz-sm" style={{ fontWeight: 650, color: "var(--ink-3)"}}>{t.tool}</span>
                {t.input?.gene && <button onClick={() => onGene(t.input.gene)} className="t-mono fz-sm" style={{ background: "transparent", color: "var(--ink)" }}>{t.input.gene}</button>}
                <span className="t-caption" style={{ color: "var(--ink-3)" }}>{summarize(t.tool, t.result)}</span>
              </div>
            </div>
          ))}
        </div>
      </details>
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
        <span className="chip" style={{ ["--tone" as any]: "var(--stone)" }}>{dive.status.replace(/_/g, " ")}</span>
        <a className="btn btn-secondary btn-sm" href="/data/pggt1b_deep_dive.json" target="_blank" rel="noreferrer" style={{ marginLeft: "auto" }}>
          JSON <ExternalLink size={13} />
        </a>
      </div>
      <p className="t-body-sm" style={{ maxWidth: "74ch", margin: 0 }}>
        {dive.prospect_read} External literature makes the prenylation mechanism plausible; it does not turn the hypothesis into biological truth.
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
      {dive.evidence_capsule && (
        <div style={{ display: "grid", gap: 10, paddingTop: 2 }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
            <div className="t-label">Evidence capsule</div>
            <span className="chip" style={{ ["--tone" as any]: "var(--moss)" }}>
              {dive.evidence_capsule.decision.replace(/_/g, " ")}
            </span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 8 }}>
            <div style={{ padding: "9px 10px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
              <div className="t-label" style={{ color: "var(--ink-3)" }}>Stim to Rest</div>
              <div className="t-mono" style={{ fontSize: 16, fontWeight: 700, marginTop: 2 }}>
                {dive.evidence_capsule.stimulated_to_rest_ratio == null ? "n/a" : `${dive.evidence_capsule.stimulated_to_rest_ratio}x`}
              </div>
              <div className="t-caption" style={{ color: "var(--ink-3)", marginTop: 2 }}>DE ratio</div>
            </div>
            <div style={{ padding: "9px 10px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
              <div className="t-label" style={{ color: "var(--ink-3)" }}>Stim to K562</div>
              <div className="t-mono" style={{ fontSize: 16, fontWeight: 700, marginTop: 2 }}>
                {dive.evidence_capsule.stimulated_to_k562_ratio == null ? "n/a" : `${dive.evidence_capsule.stimulated_to_k562_ratio}x`}
              </div>
              <div className="t-caption" style={{ color: "var(--ink-3)", marginTop: 2 }}>transfer check</div>
            </div>
            <div style={{ padding: "9px 10px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
              <div className="t-label" style={{ color: "var(--ink-3)" }}>Stim8hr balance</div>
              <div className="t-mono" style={{ fontSize: 16, fontWeight: 700, marginTop: 2 }}>
                {dive.evidence_capsule.effect_balance.Stim8hr.up_fraction}
              </div>
              <div className="t-caption" style={{ color: "var(--ink-3)", marginTop: 2 }}>up fraction</div>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
            <div>
              <div className="t-label" style={{ color: "var(--ink-3)", marginBottom: 4 }}>Evidence ladder</div>
              <div style={{ display: "grid", gap: 5 }}>
                {dive.evidence_capsule.evidence_ladder.map((step) => (
                  <p key={step.claim} className="t-caption" style={{ margin: 0 }}>
                    <span className="t-mono">{step.status}</span>: {step.claim}
                  </p>
                ))}
              </div>
            </div>
            <div>
              <div className="t-label" style={{ color: "var(--ink-3)", marginBottom: 4 }}>Missing for acceptance</div>
              <p className="t-caption" style={{ margin: 0 }}>{dive.evidence_capsule.missing_for_acceptance[0]}.</p>
            </div>
          </div>
        </div>
      )}
      {dive.matrix_slice && (
        <div style={{ display: "grid", gap: 10, paddingTop: 2 }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
            <div className="t-label">Matrix slice</div>
            <span className="chip" style={{ ["--tone" as any]: "var(--moss)" }}>
              {dive.matrix_slice.status.replace(/_/g, " ")}
            </span>
            <span className="t-caption" style={{ color: "var(--ink-3)" }}>
              {fmt(dive.matrix_slice.n_thresholded_transcripts)} moved transcripts · {fmt(dive.matrix_slice.n_up)} up · {fmt(dive.matrix_slice.n_down)} down
            </span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 10 }}>
            <div>
              <div className="t-label" style={{ color: "var(--ink-3)", marginBottom: 4 }}>Top increased</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                {dive.matrix_slice.top_up.slice(0, 8).map((row) => (
                  <button key={row.gene} onClick={() => onGene(row.gene)} className="chip" style={{ ["--tone" as any]: "var(--moss)" }}>
                    {row.gene} {row.log_fc}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <div className="t-label" style={{ color: "var(--ink-3)", marginBottom: 4 }}>Top decreased</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                {dive.matrix_slice.top_down.slice(0, 8).map((row) => (
                  <button key={row.gene} onClick={() => onGene(row.gene)} className="chip" style={{ ["--tone" as any]: "var(--cinnabar)" }}>
                    {row.gene} {row.log_fc}
                  </button>
                ))}
              </div>
            </div>
          </div>
          <p className="t-caption" style={{ margin: 0 }}>
            Trust boundary: {dive.matrix_slice.trust_boundary.replace(/_/g, " ")}. The slice supports assay design; it does not turn the hypothesis into biological truth.
          </p>
        </div>
      )}
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

function ReliabilityBenchmark() {
  const [rb, setRb] = useState<any>(null);
  useEffect(() => {
    fetch("/data/reliability_benchmark.json")
      .then((r) => (r.ok ? r.json() : null))
      .then(setRb)
      .catch(() => setRb(null));
  }, []);
  if (!rb) return null;
  const core = rb.metrics?.contradiction_rate?.pooled_core;
  const eff = rb.famous_gene_effect;
  const current = rb.current_model?.core_contradiction;
  const perModel = (rb.per_model || []).filter((m: any) => m?.core_contradiction?.checkable);
  const cal = rb.confidence_calibration?.summary;
  if (!core || !eff) return null;
  const pct = (x: number) => `${(x * 100).toFixed(1)}%`;
  return (
    <section style={{ display: "grid", gap: 12, padding: "18px 0", borderTop: "1px solid var(--rule)" }}>
      <div className="t-label">AI biology claim reliability benchmark</div>
      <h2 className="h2-app" style={{ margin: 0, maxWidth: "24ch" }}>Half of confident AI claims are contradicted by the data.</h2>
      <p className="t-body-sm" style={{ margin: 0, maxWidth: "60ch", color: "var(--ink-3)" }}>
        {core.refuted} of {core.checkable} checkable claims ({pct(core.contradiction_rate)}, 95% CI {pct(core.ci95[0])} to {pct(core.ci95[1])})
        {current ? `. A fresh Claude Opus 4.8 run: ${pct(current.contradiction_rate)}` : ""}. Every model overclaims; the strongest still 2 in 5.
      </p>
      {perModel.length > 1 && (
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {perModel.map((m: any, i: number) => (
            <span key={i} className="chip" style={{ ["--tone" as any]: "var(--stone)" }}>{m.label} {pct(m.core_contradiction.contradiction_rate)}</span>
          ))}
          {current && <span className="chip" style={{ ["--tone" as any]: "var(--cinnabar)" }}>Opus 4.8 fresh {pct(current.contradiction_rate)}</span>}
        </div>
      )}
      <p className="t-body-sm" style={{ margin: 0, maxWidth: "60ch", color: "var(--ink-3)" }}>
        Famous genes are called major regulators {pct(eff.famous_overclaim_rate)} of the time, versus {pct(eff.baseline_overclaim_rate)} for
        data-confirmed non-regulators (permutation p {eff.permutation_p_one_sided}). Stated confidence does not track correctness
        {cal ? `, overshooting the true rate by ${(cal.overconfidence_gap * 100).toFixed(1)} points` : ""}.
      </p>
      <Reproduce>
        <div><a href="/data/reliability_benchmark.json" style={{ color: "inherit" }}>/data/reliability_benchmark.json</a> · <span className="t-mono">./prospect reliability-benchmark</span></div>
        <div><a href="/data/overclaim_counter.json" style={{ color: "inherit" }}>/data/overclaim_counter.json</a> · <span className="t-mono">./prospect overclaim-counter</span></div>
      </Reproduce>
    </section>
  );
}

function Findings({ d, onGene }: { d: Data; onGene: (g: string) => void }) {
  const byKind = Object.fromEntries(d.findings.map((f) => [f.kind, f]));
  const order = ["activation_module", "regulator_vs_effector", "essentiality_artifact", "cross_cell_type_transfer", "regulon_recovery"];
  return (
    <div style={{ display: "grid", gap: 30 }}>
      <div>
        <h2 className="h1-display" style={{ marginBottom: 6 }}>Evidence</h2>
        <p className="reading" style={{ maxWidth: "56ch", fontSize: "1rem" }}>
          What the frozen data shows, and where Prospect limits its own claims.
        </p>
      </div>
      <ReliabilityBenchmark />
      {d.gse278572_comparator && (
        <section style={{ borderTop: "1px solid var(--rule)", paddingTop: 22, display: "grid", gap: 10 }}>
          <div className="t-label">Prospect corrected itself</div>
          <h2 className="h2-app" style={{ margin: 0 }}>MED12 qualifies Prospect&apos;s own read.</h2>
          <p className="t-body-sm" style={{ margin: 0, maxWidth: "60ch", color: "var(--ink-3)" }}>
            A separately frozen GSE278572 comparison shows MED12&apos;s high resting reach argues against activation specificity.
            Prospect flags its own overreach and keeps it accepted=false.
          </p>
          <Reproduce>
            <div><a href="/data/gse278572_comparator.json" style={{ color: "inherit" }}>/data/gse278572_comparator.json</a> · <span className="t-mono">python frontier/gse278572_comparator.py --check</span></div>
          </Reproduce>
        </section>
      )}
      {d.gse271788_calibration && (
        <section style={{ display: "grid", gap: 10, padding: "18px 0", borderTop: "1px solid var(--rule)" }}>
          <div className="t-label">Independent primary-CD4 calibration</div>
          <h2 className="h2-app" style={{ margin: 0, maxWidth: "28ch" }}>Broad reach carries across studies; the narrow claim does not.</h2>
          <p className="t-body-sm" style={{ margin: 0, maxWidth: "60ch", color: "var(--ink-3)" }}>
            Across {d.gse271788_calibration.primary_result.n} shared perturbations, broad reach agrees with an independent study
            (Spearman rho {d.gse271788_calibration.primary_result.spearman_rho.toFixed(3)}, p {d.gse271788_calibration.primary_result.permutation_p_value_one_sided.toFixed(4)}, all three kills pass).
            The narrower activation-specific claim fails four of five kills, so it does not clear the pre-registered bar. accepted=false.
          </p>
          <Reproduce>
            <div><a href="/data/gse271788_calibration.json" style={{ color: "inherit" }}>/data/gse271788_calibration.json</a> · <a href="/data/gse271788_activation_specificity.json" style={{ color: "inherit" }}>/data/gse271788_activation_specificity.json</a></div>
            <div><span className="t-mono">python frontier/gse271788_activation_specificity.py --check</span></div>
          </Reproduce>
        </section>
      )}
      <details className="reproduce" style={{ borderTop: "1px solid var(--rule)", paddingTop: 16 }}>
        <summary>The five signed CD4+ findings, in detail</summary>
        <div style={{ display: "grid", gap: 26, marginTop: 16 }}>
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
                  <span key={x.gene} className="chip" style={{ ["--tone" as any]: "var(--stone)" }}>{x.gene}</span>
                ))}
              </div>
            </section>
          )}
        </div>
      </details>
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
            Five reproduced finding objects, ordered for the demo: recover known biology, limit broad driver claims,
            qualify Rest reach, compare cell contexts, then recover regulons.
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
        Source <span className="t-mono">{index.source}</span>. Replay <span className="t-mono">./prospect findings-index</span>.
        The index summarizes signed objects; evidence tables below carry the numbers.
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
            background: x.d === "up" ? "var(--state-reproduced-tint)" : "var(--state-refuted-tint)",
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
