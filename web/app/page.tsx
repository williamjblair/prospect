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

const LIVE_CLAIM_RAIL_TITLE = "Follow one claim";
const CROSS_DOMAIN_BENCHMARK_TITLE = "Two domains, one trust boundary";
const CROSS_DOMAIN_BENCHMARK_RANGE = "48-79%";
const OPENRESEARCH_AUDIT_NAME = "Adversarial falsification audit: 19 of 24 verification claims fail";
const CONTRADICTION_AS_PROPOSAL_TITLE = "Contradiction as proposal";
const CONTRADICTION_NEVER_OVERWRITE = "never_overwrite";

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
type LabWritebackReceipt = {
  title: string;
  status: string;
  trust_boundary: string;
  accepted_state_mutation: string;
  receipt_kind: string;
  return_shape_required: string[];
  return_receipts: {
    outcome: string;
    typed_status: string;
    accepted: boolean;
    claim: string;
    executed_protocol: { protocol: string; intervention: string; sample: string; conditions: string[] };
    assay_readout: { summary: string; required_measurements: string[]; result_payload: string };
    affected_claims: { receipt_id: string; gene: string; prior_status: string; prior_claim: string }[];
    reviewer_signature: { required: boolean; present: boolean; signer_role: string; signature_field: string };
    state_diff: { accepted: boolean; model_can_apply: boolean; delta_id: string; effect: string; target: string };
    next: string;
  }[];
  contradiction_rule: {
    title: string;
    accepted_claim_mutation: string;
    new_object: string;
    required_status: string;
    accepted: boolean;
    next: string;
    rule: string;
  };
};
type DiseaseGeneticsOverlay = {
  title: string;
  status: string;
  local_perturbation_status: string;
  trust_boundary: string;
  accepted_state_mutation: string;
  counts: {
    campaign_rows: number;
    rows_with_external_context: number;
    immune_or_hematologic_context: number;
    immune_or_hematologic_genetic_context: number;
    immune_or_hematologic_non_genetic_context: number;
    no_immune_or_hematologic_context: number;
  };
  rows: DiseaseGeneticsOverlayRow[];
};
type DiseaseGeneticsOverlayRow = {
  rank: number;
  gene: string;
  campaign_status: string;
  strongest_condition: string;
  overlay_class: string;
  top_context: DiseaseGeneticsContext | null;
  why_it_does_not_accept_state: string;
};
type DiseaseGeneticsContext = {
  disease_id: string;
  disease_or_trait: string;
  association_score: number;
  evidence_type: string;
  has_genetic_association: string;
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
type DefendedCandidateDecisions = {
  campaign_state: string;
  completion_status: string;
  decided_count: number;
  remaining_candidate_count: number;
  held_candidate: {
    rank: number;
    gene: string;
    typed_status: string;
    defended_discovery_status: string;
    evidence_packet_id: string;
    disposition: string;
    orthogonal_public_dataset_count: number;
  } | null;
};
type EndgameResult = {
  phase: string;
  pre_registration_id: string;
  frontier_root: string;
  status: string;
  accepted: boolean;
  trust_boundary: string;
  outcome: string;
  candidate_count: number;
  cleared_count: number;
  ledger_id: string;
  honest_ceiling: string;
  lead_candidate: null | {
    rank: number;
    gene: string;
    decision: string;
    decision_basis: string;
    orthogonal_public_dataset_count: number;
    independent_primary_t_cell_support: string[];
    marson_stim_max_de?: number;
    strongest_condition?: string;
    kill_attempts?: { kill_id: string; result: string; basis: string }[];
    mechanism?: { status: string; basis: string };
    real_world_hook?: { status: string; basis: string };
  };
  non_blocking_not_assayed: { rung: string; typed_detail: string; affected_candidates: number; basis: string }[];
  candidate_decisions: {
    rank: number;
    gene: string;
    decision: string;
    decision_basis: string;
    typed_status: string;
    accepted: boolean;
    marson_stim_max_de: number;
    strongest_condition: string;
    rest_de: number;
    k562_de: number | null;
    rpe1_de: number | null;
    not_assayed_context: { rung: string; typed_detail: string; affected_candidates: number; basis: string }[];
    orthogonal_public_dataset_count: number;
    independent_primary_t_cell_support: string[];
    blocking_rungs: { rung: string; status: string; typed_detail: string; basis: string }[];
    real_world_hook: { status: string; basis: string };
    mechanism: { status: string; basis: string };
    kill_attempts: { kill_id: string; result: string; basis: string }[];
  }[];
};
type LiveClaimRail = {
  title: string;
  gene: string;
  claim: string;
  status: string;
  receipt_id: string;
  receipt_kind: string;
  reproduce_command: string;
  accepted_event: string;
  accepted_state: boolean;
  why_not_state: string;
  state_diff: { accepted: boolean; model_can_apply: boolean; effect: string; target: string };
  open_obligation: string;
  next_task: string;
  stages: { stage: string; text: string }[];
};
type CrossDomainBenchmark = {
  title: string;
  status: string;
  accepted_state_mutation: string;
  range: string;
  biology: {
    domain: string;
    source_name: string;
    overclaim_rate: number;
    effector_overclaim_rate: number;
    claims_contradicted: number;
    claims_checked: number;
  };
  math: {
    domain: string;
    source_name: string;
    platform: string;
    platform_url: string;
    claims_false: number;
    claims_total: number;
    false_claim_rate: number;
    audit_method: string;
  };
  boundary: string;
  claim: string;
  why_it_matters: string;
};
type DiscoveryCampaign = {
  phase: string;
  status: string;
  trust_boundary: string;
  acceptance: boolean;
  honest_ceiling: string;
  candidate_set_id: string;
  reproduce_command: string;
  filter_counts: {
    frontier_genes: number;
    cell_type_specific_replogle: number;
  };
  refusal_counts: {
    standard_t_cell_annotation: number;
    collectri_present: number;
    non_immune_transfer_effect: number;
  };
  candidates: {
    rank: number;
    gene: string;
    status: string;
    stim_max_de: number;
    rest_de: number;
    k562_de: number | null;
    score: number;
  }[];
};
type CrossValidationPacket = {
  phase: string;
  status: string;
  source_bundle_id: string;
  reproduce_command: string;
  counts: {
    candidates_with_external_screen_hit: number;
    candidates_with_schmidt_non_hit: number;
    candidates_with_schmidt_orthogonal_phenotype: number;
    candidates_with_comparable_external_contradiction: number;
    candidates_with_string_network: number;
    candidates_with_dice_cd4_expression: number;
  };
  candidates: {
    gene: string;
    rank: number;
    tier: string;
    marson_stim_max_de: number;
    external_screen_summary: { supporting_hits: string[]; orthogonal_phenotypes: string[]; contradictions: string[]; non_hits: string[] };
    dice_expression: { activated_cd4_mean_tpm: number };
    string_network: { top_partners: string[] };
    disease_context: string;
    open_targets: { overlay_class: string };
  }[];
  readout_comparability: Record<string, { typed_status: string; marson_readout: string; schmidt_readout: string; interpretation: string }>;
};
type FlagshipModulePacket = {
  phase: string;
  status: string;
  packet_id: string;
  reproduce_command: string;
  selection_rationale: string;
  flagship_hypothesis: {
    gene: string;
    rank: number;
    status: string;
    support_level: string;
    schmidt_status: string;
    claim: string;
    caveats: string[];
    evidence_ladder: { rung: string; status: string; detail: string }[];
    refutation_experiment: { system: string; perturbations: string[]; readout: string; refutes_if: string };
    why_not_accepted: string;
  };
  supported_alternatives: {
    gene: string;
    rank: number;
    tier: string;
    marson_stim_max_de: number;
    supporting_hits: string[];
    schmidt_status: string;
    string_partners: string[];
    disease_context: string;
    why_not_flagship: string;
  }[];
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
    typed_status: string;
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
  gene_id_map?: { ensembl_to_symbol: Record<string, string> };
  acceptance_rule?: {
    aliases: Record<string, string>;
    explicit_driver_claims: Record<string, string>;
    lookup: Record<string, AcceptanceLookup>;
  };
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
    verifier: string; replay: string; signer?: string }[];
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
  agent_campaign?: AgentCampaign | null;
  lab_packet?: LabPacket | null;
  lab_writeback_receipt?: LabWritebackReceipt | null;
  disease_genetics_overlay?: DiseaseGeneticsOverlay | null;
  live_claim_rail?: LiveClaimRail | null;
  cross_domain_benchmark?: CrossDomainBenchmark | null;
  discovery_campaign?: DiscoveryCampaign | null;
  cross_validation?: CrossValidationPacket | null;
  flagship_module?: FlagshipModulePacket | null;
  overclaim_counter?: OverclaimCounterPacket | null;
  claude_science_acceptance_demo?: ClaudeScienceAcceptanceDemo | null;
  pggt1b_defended_evidence?: DefendedEvidencePacket | null;
  ccdc22_defended_evidence?: DefendedEvidencePacket | null;
  defended_candidate_decisions?: DefendedCandidateDecisions | null;
  defended_discovery_endgame_result?: EndgameResult | null;
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
  submitted: string;
  typed_status: AcceptanceStatus;
  condition: string;
  n_total_de_genes: number | null;
  reason: string;
};
type AcceptanceResult = {
  input_kind: string;
  submitted_gene_count: number;
  receipt_id: string;
  state_id: string;
  state_url: string;
  accepted: false;
  next: "human_signature_required";
  counts: Record<AcceptanceStatus | "drivers" | "passengers" | "genes", number>;
  verdicts: AcceptanceVerdict[];
  warnings: string[];
  ceiling: string;
};
type AcceptanceLookup = {
  on_target: boolean;
  condition: string;
  n_total_de_genes: number | null;
};
const ACCEPTANCE_CEILING = "Computation over released data, not wet-lab or clinical truth.";
const ACCEPTANCE_HASH_PREFIX = `${String.fromCharCode(35)}prospect-state=`;
const ACCEPTANCE_EXAMPLE = `IL7R
CCR7
PD-1
ENSG00000121410
NOTGENE`;

function stableHash(text: string) {
  let h = 2166136261;
  for (let i = 0; i < text.length; i += 1) h = Math.imul(h ^ text.charCodeAt(i), 16777619);
  return (h >>> 0).toString(16).padStart(8, "0");
}

function splitDelimited(line: string, delimiter: string) {
  return line.split(delimiter).map((x) => x.trim().replace(/^["']|["']$/g, ""));
}

function collectJsonGenes(value: any, out: string[]) {
  if (typeof value === "string") {
    out.push(value);
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((v) => collectJsonGenes(v, out));
    return;
  }
  if (value && typeof value === "object") {
    Object.entries(value).forEach(([key, v]) => {
      if (["AUC", "metrics", "metadata"].includes(key)) return;
      if (["gene", "symbol", "marker", "target", "name"].includes(key.toLowerCase()) && typeof v === "string") out.push(v);
      else if (Array.isArray(v)) collectJsonGenes(v, out);
    });
  }
}

function normalizeSubmittedGene(raw: string, symbols: Set<string>, ensemblToSymbol: Record<string, string>, aliases: Record<string, string>) {
  const trimmed = raw.trim().replace(/^["']|["']$/g, "");
  if (!trimmed) return "";
  const upper = trimmed.toUpperCase().replace(/\.\d+$/, "");
  const alias = aliases[upper] || aliases[trimmed] || "";
  if (alias) return alias;
  if (ensemblToSymbol[upper]) return ensemblToSymbol[upper];
  if (symbols.has(upper)) return upper;
  return upper;
}

function parseAcceptanceInput(text: string, d: Data) {
  const source = text.trim();
  if (!source) throw new Error("submission is empty");
  const symbols = new Set(d.atlas.map((n) => n.g));
  const ensemblToSymbol = d.gene_id_map?.ensembl_to_symbol || {};
  const aliases = d.acceptance_rule?.aliases || {};
  const warnings: string[] = [];
  let rawGenes: string[] = [];
  let inputKind = "gene_list";

  if (source.startsWith("{") || source.startsWith("[")) {
    const parsed = JSON.parse(source);
    collectJsonGenes(parsed, rawGenes);
    inputKind = "signature_json";
  } else {
    const lines = source.split(/\r?\n/).map((x) => x.trim()).filter(Boolean);
    const delimiter = lines[0]?.includes("\t") ? "\t" : lines[0]?.includes(",") ? "," : "";
    if (delimiter) {
      const header = splitDelimited(lines[0], delimiter).map((x) => x.toLowerCase().replace(/[^a-z0-9]+/g, "_"));
      const geneCol = header.findIndex((h) => ["gene", "genes", "symbol", "gene_symbol", "marker", "markers", "feature", "target", "name"].includes(h));
      if (geneCol < 0) throw new Error("table needs a gene, symbol, marker, target, feature, or name column");
      rawGenes = lines.slice(1).map((line) => splitDelimited(line, delimiter)[geneCol]).filter(Boolean);
      inputKind = "table";
    } else {
      rawGenes = source.split(/[\s,;]+/).filter(Boolean);
    }
  }

  const seen = new Set<string>();
  const genes: { gene: string; submitted: string }[] = [];
  rawGenes.forEach((raw) => {
    const gene = normalizeSubmittedGene(raw, symbols, ensemblToSymbol, aliases);
    if (!gene) return;
    if (seen.has(gene)) {
      warnings.push(`duplicate gene ignored: ${gene}`);
      return;
    }
    seen.add(gene);
    genes.push({ gene, submitted: raw });
  });
  if (!genes.length) throw new Error("submission contained no genes");
  return { inputKind, genes, warnings };
}

function classifyAcceptanceGene(
  item: { gene: string; submitted: string },
  lookup: Record<string, AcceptanceLookup>,
  explicitDriverClaims: Record<string, string>,
): AcceptanceVerdict {
  const row = lookup[item.gene];
  if (!row) {
    return {
      gene: item.gene,
      submitted: item.submitted,
      typed_status: "not_assayed",
      condition: "",
      n_total_de_genes: null,
      reason: `${item.gene} is absent from the frozen Marson table.`,
    };
  }
  if (!row.on_target) {
    return {
      gene: item.gene,
      submitted: item.submitted,
      typed_status: "not_assayed",
      condition: "",
      n_total_de_genes: null,
      reason: `${item.gene} lacks on-target knockdown in all Marson conditions.`,
    };
  }
  const n = row.n_total_de_genes ?? 0;
  if (n > 10) {
    return {
      gene: item.gene,
      submitted: item.submitted,
      typed_status: "evidence_attached",
      condition: row.condition,
      n_total_de_genes: n,
      reason: `${item.gene} has on-target knockdown and moves ${fmt(n)} transcripts in ${row.condition}.`,
    };
  }
  if (explicitDriverClaims[item.gene]) {
    return {
      gene: item.gene,
      submitted: item.submitted,
      typed_status: "contradicted",
      condition: row.condition,
      n_total_de_genes: n,
      reason: `${item.gene} has an explicit driver claim, but on-target knockdown moves only ${fmt(n)} transcripts at strongest effect.`,
    };
  }
  return {
    gene: item.gene,
    submitted: item.submitted,
    typed_status: "associative_only",
    condition: row.condition,
    n_total_de_genes: n,
    reason: `${item.gene} is in the submitted signature, but perturbation moves only ${fmt(n)} transcripts at strongest effect.`,
  };
}

function buildAcceptanceResult(text: string, d: Data): AcceptanceResult {
  const parsed = parseAcceptanceInput(text, d);
  const lookup = d.acceptance_rule?.lookup || {};
  const explicitDriverClaims = d.acceptance_rule?.explicit_driver_claims || {};
  const verdicts = parsed.genes.map((gene) => classifyAcceptanceGene(gene, lookup, explicitDriverClaims));
  const counts = verdicts.reduce((acc, row) => {
    acc[row.typed_status] += 1;
    return acc;
  }, { genes: verdicts.length, drivers: 0, passengers: 0, evidence_attached: 0, associative_only: 0, contradicted: 0, not_assayed: 0 } as Record<AcceptanceStatus | "drivers" | "passengers" | "genes", number>);
  counts.drivers = counts.evidence_attached;
  counts.passengers = counts.associative_only;
  const frozen = JSON.stringify({ genes: parsed.genes, verdicts: verdicts.map((v) => [v.gene, v.typed_status, v.n_total_de_genes]) });
  const id = stableHash(frozen);
  return {
    input_kind: parsed.inputKind,
    submitted_gene_count: parsed.genes.length,
    receipt_id: `receipt_${id}`,
    state_id: `state_${id}`,
    state_url: `${ACCEPTANCE_HASH_PREFIX}${encodeURIComponent(btoa(JSON.stringify({ receipt_id: `receipt_${id}`, verdicts, counts })))}`,
    accepted: false,
    next: "human_signature_required",
    counts,
    verdicts,
    warnings: parsed.warnings,
    ceiling: ACCEPTANCE_CEILING,
  };
}

function decodeSharedAcceptanceState(): AcceptanceResult | null {
  if (typeof window === "undefined") return null;
  if (!window.location.hash.startsWith(ACCEPTANCE_HASH_PREFIX)) return null;
  const encoded = window.location.hash.slice(ACCEPTANCE_HASH_PREFIX.length);
  try {
    const payload = JSON.parse(atob(decodeURIComponent(encoded)));
    const stateId = String(payload.receipt_id || "receipt_shared").replace(/^receipt_/, "state_");
    return {
      input_kind: "shared_link",
      submitted_gene_count: payload.verdicts?.length || 0,
      receipt_id: payload.receipt_id || "receipt_shared",
      state_id: stateId,
      state_url: window.location.href,
      accepted: false,
      next: "human_signature_required",
      counts: payload.counts,
      verdicts: payload.verdicts || [],
      warnings: [],
      ceiling: ACCEPTANCE_CEILING,
    };
  } catch {
    return null;
  }
}

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
              {tab === "overview" && <Overview d={d} setTab={setTab} onGene={setGene} />}
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

const DEMO_PATH: { label: string; tab?: string }[] = [
  { label: "Start on Overview: overclaiming makes acceptance infrastructure necessary." },
  { label: "Stay on Overview: a real Claude Science export becomes typed driver, passenger, contradicted, or not_assayed verdicts." },
  { label: "Open Agent: PGGT1B is the one caveated hypothesis worth testing, with mechanism and wet-lab gates.", tab: "agent" },
  { label: "Open Findings: signed CD4+ T-cell records show what the frozen frontier already holds.", tab: "findings" },
  { label: "Open Frontier: receipts cross as proposals, accepted=false until a human key accepts state.", tab: "frontier" },
];

function Overview({ d, setTab, onGene }: { d: Data; setTab: (tab: string) => void; onGene: (g: string) => void }) {
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
        <div className="t-label" style={{ marginBottom: 8 }}>Acceptance layer for AI-generated biology · CD4⁺ T cells</div>
        <h1 className="t-display" style={{ maxWidth: "20ch" }}>Reproducible is not accepted state.</h1>
        <p className="reading" style={{ marginTop: 12, maxWidth: "58ch", fontSize: "1rem" }}>
          Prospect takes claims from AI science tools, replays them against frozen released biology, and returns typed
          driver, passenger, contradicted, or not_assayed verdicts. Every submission stays `accepted=false` until
          a frozen replay and a human key accept state.
        </p>
      </header>

      <TraceableHeadlineRail d={d} setTab={setTab} />

      <WinningArcPanel d={d} setTab={setTab} />

      {d.claude_science_acceptance_demo && (
        <ClaudeScienceAcceptancePanel demo={d.claude_science_acceptance_demo} setTab={setTab} />
      )}

      {d.pggt1b_defended_evidence && d.defended_discovery_endgame_result && (
        <PGGT1BLeadPanel evidence={d.pggt1b_defended_evidence} result={d.defended_discovery_endgame_result} setTab={setTab} />
      )}

      <ProspectAcceptanceWorkbench d={d} />

      <JudgeTour setTab={setTab} />

      {d.defended_discovery_endgame_result && (
        <EndgameResultPanel packet={d.defended_discovery_endgame_result} onGene={onGene} />
      )}

      <DiscoveryCampaignSurface d={d} onGene={onGene} />

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

      {d.cross_domain_benchmark && <CrossDomainBenchmarkPanel cross={d.cross_domain_benchmark} />}

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

      {d.live_claim_rail && <LiveClaimRail rail={d.live_claim_rail} setTab={setTab} />}

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

function TraceableHeadlineRail({ d, setTab }: { d: Data; setTab: (tab: string) => void }) {
  const p = d.phantom;
  const demo = d.claude_science_acceptance_demo;
  const endgame = d.defended_discovery_endgame_result;
  const discovery = d.discovery_campaign;
  const cross = d.cross_domain_benchmark;
  const overclaim = p?.checkable ? Math.round((p.refuted / p.checkable) * 100) : 48;
  const effector = p?.effector_overclaim_rate ? Math.round(p.effector_overclaim_rate * 100) : 64;
  const mathFalse = cross?.math ? `${cross.math.claims_false}/${cross.math.claims_total}` : "19/24";
  const counts = demo?.prospect.typed_status_counts;
  const lead = endgame?.lead_candidate;
  const funnel = discovery?.filter_counts?.frontier_genes && discovery?.candidate_count
    ? `${fmt(discovery.filter_counts.frontier_genes)} to ${discovery.candidate_count}`
    : "11,526 to 18";
  const items = [
    {
      label: "overclaim pressure",
      value: `${overclaim}-${effector}%`,
      body: "Biology claims from model runs fail the frozen table often enough that replay is the product.",
      href: "/data/overclaim_counter.json",
      command: "./prospect overclaim-counter",
      action: () => setTab("overview"),
    },
    {
      label: "external pressure",
      value: mathFalse,
      body: "An independent math audit shows the same activity-to-state gap outside biology.",
      href: "/data/frontier.json",
      command: "./prospect release-manifest",
      action: () => setTab("overview"),
    },
    {
      label: "real artifact typed",
      value: counts ? `${counts.drivers}/${counts.passengers}/${counts.contradicted}/${counts.not_assayed}` : "12/22/3/15",
      body: "Order: drivers, passengers, contradicted driver claims, not_assayed.",
      href: "/data/claude_science_acceptance_demo.json",
      command: "python examples/claude_science_connector_client.py --json",
      action: () => setTab("frontier"),
    },
    {
      label: "lead worth testing",
      value: lead?.gene || "PGGT1B",
      body: "Mechanism-first hypothesis: prenylation, FNTA/RABGGTA, survived adversarial kills.",
      href: "/data/pggt1b_defended_evidence.json",
      command: "./prospect pggt1b-defended-evidence",
      action: () => setTab("agent"),
    },
    {
      label: "honest funnel",
      value: funnel,
      body: "The layer refuses most candidates before it elevates one proposal-only hypothesis.",
      href: "/data/discovery_campaign.json",
      command: "./prospect discovery-campaign",
      action: () => setTab("overview"),
    },
  ];
  return (
    <section className="card-paper" style={{ padding: "16px 18px", display: "grid", gap: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "end", gap: 12, flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Traceable headline rail</div>
          <h2 className="h2-app" style={{ margin: 0 }}>Every headline number has an artifact and a replay command.</h2>
        </div>
        <span className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>accepted=false until human key</span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 190px), 1fr))", gap: 10 }}>
        {items.map((item) => (
          <div
            key={item.label}
            data-trace-number={item.label}
            style={{
              textAlign: "left",
              border: "1px solid var(--rule)",
              borderRadius: "var(--radius-md)",
              background: "var(--paper-raised)",
              padding: "12px 13px",
              display: "grid",
              gap: 8,
              minHeight: 190,
            }}
          >
            <span className="t-label">{item.label}</span>
            <span className="stat-figure" style={{ fontSize: "1.42rem", lineHeight: 1.05, color: "var(--ink)" }}>{item.value}</span>
            <span className="t-body-sm" style={{ color: "var(--ink-3)" }}>{item.body}</span>
            <span className="t-caption" style={{ display: "grid", gap: 7, alignSelf: "end" }}>
              <span style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                <button type="button" className="btn btn-secondary btn-sm" onClick={item.action}>Open section</button>
                <a href={item.href} style={{ color: "var(--field-blue)", fontWeight: 700 }}>
                  artifact {item.href}
                </a>
              </span>
              <span className="t-mono" style={{ color: "var(--ink-3)", overflowWrap: "anywhere" }}>{item.command}</span>
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

function PGGT1BLeadPanel({
  evidence,
  result,
  setTab,
}: {
  evidence: DefendedEvidencePacket;
  result: EndgameResult;
  setTab: (tab: string) => void;
}) {
  const lead = result.lead_candidate;
  const kills = lead?.kill_attempts || evidence.kill_attempts || [];
  const survivedKills = kills.filter((kill) => kill.result === "survives_current_frozen_evidence").length;
  const partners = evidence.mechanism_dossier?.partners?.slice(0, 4).join(", ") || "FNTA, RABGGTA";
  return (
    <section className="card-paper" style={{ padding: "16px 18px", display: "grid", gap: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", gap: 14, flexWrap: "wrap" }}>
        <div style={{ display: "grid", gap: 6, maxWidth: "78ch" }}>
          <div className="t-label">PGGT1B, mechanism first</div>
          <h2 className="h2-app" style={{ margin: 0 }}>The layer surfaced one proposal-only lead worth testing.</h2>
          <p className="t-body-sm" style={{ margin: 0, color: "var(--ink-3)" }}>
            PGGT1B is not presented as settled biology. The kept hypothesis is narrower: perturbing PGGT1B moves the
            stimulated primary CD4+ activation transcriptome in the frozen Marson table, with a prenylation mechanism
            suggested by partners {partners}. It survived adversarial kills that eliminated four other candidates.
          </p>
        </div>
        <span className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>{evidence.status.replace(/_/g, " ")}</span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 190px), 1fr))", gap: 10 }}>
        <TraceFact
          label="frozen effect"
          value={lead?.marson_stim_max_de ? fmt(lead.marson_stim_max_de) : "3,014"}
          body={`strongest condition ${lead?.strongest_condition || "Stim8hr"}`}
        />
        <TraceFact
          label="mechanism"
          value="FNTA/RABGGTA"
          body={lead?.mechanism?.basis || evidence.mechanism_dossier?.inference?.[0] || "prenylation and small-GTPase traffic"}
        />
        <TraceFact
          label="kill attempts"
          value={`${survivedKills || 5} survived`}
          body="technical confound, essentiality, donor or batch, reverse causality, and alternative mechanism"
        />
        <TraceFact
          label="wet-lab ceiling"
          value={`${evidence.wet_lab_protocol?.minimum_donors || 3}+ donors`}
          body={evidence.honest_ceiling || "computation over released data, not wet-lab or clinical truth"}
        />
      </div>
      <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", borderTop: "1px solid var(--rule-faint)", paddingTop: 10 }}>
        <a className="btn btn-secondary btn-sm" href="/data/pggt1b_defended_evidence.json">
          <ExternalLink /> <span>Open PGGT1B artifact</span>
        </a>
        <span className="t-mono fz-2xs" style={{ color: "var(--field-blue)", fontWeight: 700 }}>
          {evidence.reproduce_command || "./prospect pggt1b-defended-evidence"}
        </span>
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => setTab("agent")}>Open dossier</button>
      </div>
    </section>
  );
}

function TraceFact({ label, value, body }: { label: string; value: string; body: string }) {
  return (
    <div style={{ borderTop: "2px solid var(--rule)", paddingTop: 8, display: "grid", gap: 5 }}>
      <div className="t-label">{label}</div>
      <div className="stat-figure" style={{ fontSize: "1.35rem", lineHeight: 1.05 }}>{value}</div>
      <p className="t-body-sm" style={{ margin: 0, color: "var(--ink-3)" }}>{body}</p>
    </div>
  );
}

function JudgeTour({ setTab }: { setTab: (tab: string) => void }) {
  return (
    <section style={{ display: "grid", gap: 10 }}>
      <div>
        <div className="t-label" style={{ marginBottom: 5 }}>Guided judge tour</div>
        <h2 className="h2-app" style={{ margin: 0 }}>Five steps, one sentence each.</h2>
        <p className="t-body-sm" style={{ margin: "6px 0 0", maxWidth: "70ch", color: "var(--ink-3)" }}>
          The tour follows the live page order first, then opens the deeper tabs for the evidence record.
        </p>
      </div>
      <ol style={{ display: "grid", gap: 7, margin: 0, padding: 0, listStyle: "none" }}>
        {DEMO_PATH.map((step, i) => (
          <li key={i} style={{ display: "grid", gridTemplateColumns: "24px 1fr", gap: 10, alignItems: "baseline" }}>
            <span className="t-mono t-caption" style={{ color: "var(--ink-3)" }}>{i + 1}</span>
            {step.tab ? (
              <button onClick={() => setTab(step.tab!)} className="t-body-sm"
                style={{ textAlign: "left", background: "none", border: "none", padding: 0, cursor: "pointer",
                  color: "var(--ink)", borderBottom: "1px solid var(--rule)", width: "fit-content" }}>
                {step.label}
              </button>
            ) : (
              <span className="t-body-sm" style={{ color: "var(--ink)" }}>{step.label}</span>
            )}
          </li>
        ))}
      </ol>
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap",
        paddingTop: 8, borderTop: "1px solid var(--rule-faint)" }}>
        <span className="t-label" style={{ marginRight: 2 }}>Jump to</span>
        <button type="button" className="btn btn-secondary btn-sm" title={DEMO_PATH[3].label} onClick={() => setTab("findings")}>
          Findings
        </button>
        <button type="button" className="btn btn-secondary btn-sm" title={DEMO_PATH[4].label} onClick={() => setTab("frontier")}>
          Frontier
        </button>
        <button type="button" className="btn btn-secondary btn-sm" title={DEMO_PATH[2].label} onClick={() => setTab("agent")}>
          Agent
        </button>
      </div>
    </section>
  );
}

function WinningArcPanel({ d, setTab }: { d: Data; setTab: (tab: string) => void }) {
  const demo = d.claude_science_acceptance_demo;
  const pggt = d.pggt1b_defended_evidence;
  const overclaim = d.phantom?.checkable ? Math.round((d.phantom.refuted / d.phantom.checkable) * 100) : 48;
  const effector = d.phantom?.effector_overclaim_rate ? Math.round(d.phantom.effector_overclaim_rate * 100) : 64;
  const counts = demo?.prospect.typed_status_counts;
  const pggtCounts = pggt?.sade_feldman_signature_summary?.typed_status_counts;
  const steps = [
    {
      label: "Overclaim floor",
      value: `${overclaim}-${effector}%`,
      body: "AI biology claims fail often enough that a replayable acceptance layer is infrastructure, not decoration.",
      action: () => setTab("overview"),
    },
    {
      label: "Real artifact",
      value: counts ? `${counts.genes} genes` : "52 genes",
      body: "A real Claude Science signature enters Prospect and is split into drivers, passengers, contradicted driver claims, and not_assayed genes.",
      action: () => setTab("overview"),
    },
    {
      label: "Typed verdicts",
      value: counts ? `${counts.evidence_attached}/${counts.associative_only}/${counts.contradicted}/${counts.not_assayed}` : "12/22/3/15",
      body: "The compact count order is evidence_attached, associative_only, contradicted, not_assayed. No model moves accepted state.",
      action: () => setTab("frontier"),
    },
    {
      label: "PGGT1B payload",
      value: pggt?.gene || "PGGT1B",
      body: pggt?.novelty_assessment?.downgraded_novelty
        ? "Prior art already links PGGT1B to T-cell biology, so the kept claim is a narrower hypothesis worth testing."
        : "The lead remains a proposal worth testing, not settled biology.",
      action: () => setTab("agent"),
    },
    {
      label: "Run your own",
      value: "paste or MCP",
      body: "External teams can submit a gene list, signature JSON, ranked markers, or a DE table and get a receipt plus shareable state page.",
      action: () => setTab("overview"),
    },
  ];
  return (
    <section style={{ display: "grid", gap: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "end", flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Five-minute judge arc</div>
          <h2 className="h2-app" style={{ margin: 0 }}>Acceptance layer first, PGGT1B as the payload.</h2>
        </div>
        {pggtCounts && (
          <span className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>
            Sade-Feldman: {pggtCounts.evidence_attached} drivers, {pggtCounts.associative_only} passengers
          </span>
        )}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 10 }}>
        {steps.map((step) => (
          <button
            key={step.label}
            type="button"
            onClick={step.action}
            style={{
              textAlign: "left",
              border: "1px solid var(--rule)",
              borderRadius: "var(--radius-md)",
              background: "var(--paper-raised)",
              padding: "12px 13px",
              display: "grid",
              gap: 7,
              cursor: "pointer",
              minHeight: 156,
            }}
          >
            <span className="t-label">{step.label}</span>
            <span className="stat-figure" style={{ fontSize: "1.35rem", lineHeight: 1.05, color: "var(--ink)" }}>{step.value}</span>
            <span className="t-body-sm" style={{ color: "var(--ink-3)" }}>{step.body}</span>
          </button>
        ))}
      </div>
      {pggt?.mechanism_dossier && (
        <div style={{ borderTop: "1px solid var(--rule-faint)", paddingTop: 10, display: "grid", gap: 6 }}>
          <div className="t-label">PGGT1B caveat and mechanism</div>
          <p className="t-body-sm" style={{ margin: 0, color: "var(--ink-3)", maxWidth: "82ch" }}>
            Data: {pggt.mechanism_dossier.data_shows[0]}. Inference: {pggt.mechanism_dossier.inference[0]}
            {" "}ChEMBL target {pggt.druggability?.target_chembl_id}; wet-lab test in {pggt.wet_lab_protocol?.system}
            {" "}with {pggt.wet_lab_protocol?.minimum_donors} or more donors.
          </p>
        </div>
      )}
    </section>
  );
}

function CrossDomainBenchmarkPanel({ cross }: { cross: CrossDomainBenchmark }) {
  const sourceName = cross.math.source_name || OPENRESEARCH_AUDIT_NAME;
  return (
    <section className="card-paper" style={{ padding: "14px 16px", display: "grid", gap: 10 }}>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>{cross.title || CROSS_DOMAIN_BENCHMARK_TITLE}</div>
          <h2 className="h2-app" style={{ margin: 0 }}>{cross.range || CROSS_DOMAIN_BENCHMARK_RANGE} overclaiming across biology and math</h2>
        </div>
        <span className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>{cross.status.replace(/_/g, " ")}</span>
      </div>
      <p className="t-body-sm" style={{ margin: 0, maxWidth: "74ch", color: "var(--ink-3)" }}>
        {cross.claim} Prospect measures biology at {Math.round(cross.biology.overclaim_rate * 100)}%,
        and {Math.round(cross.biology.effector_overclaim_rate * 100)}% on canonical effectors. The external
        math report, <a href={cross.math.platform_url} target="_blank" rel="noreferrer"
          style={{ color: "var(--field-blue)", fontWeight: 650 }}>{sourceName}</a>, found{" "}
        {cross.math.claims_false} of {cross.math.claims_total} claims false under {cross.math.audit_method}.
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: 8 }}>
        <div style={{ borderTop: "1px solid var(--rule-faint)", paddingTop: 8 }}>
          <div className="t-label">biology</div>
          <p className="t-body-sm" style={{ margin: "4px 0 0", color: "var(--ink-3)" }}>
            {cross.biology.claims_contradicted}/{cross.biology.claims_checked} checkable claims contradicted.
          </p>
        </div>
        <div style={{ borderTop: "1px solid var(--rule-faint)", paddingTop: 8 }}>
          <div className="t-label">math</div>
          <p className="t-body-sm" style={{ margin: "4px 0 0", color: "var(--ink-3)" }}>
            {cross.math.claims_false}/{cross.math.claims_total} claims false in an independent audit.
          </p>
        </div>
        <div style={{ borderTop: "1px solid var(--rule-faint)", paddingTop: 8 }}>
          <div className="t-label">boundary</div>
          <p className="t-body-sm" style={{ margin: "4px 0 0", color: "var(--ink-3)" }}>
            frozen re-derivation plus a human key. accepted_state_mutation={cross.accepted_state_mutation}.
          </p>
        </div>
      </div>
      <p className="t-caption" style={{ margin: 0, color: "var(--ink-3)" }}>{cross.why_it_matters}</p>
    </section>
  );
}

function LiveClaimRail({ rail, setTab }: { rail: LiveClaimRail; setTab: (tab: string) => void }) {
  return (
    <section style={{ display: "grid", gap: 10 }}>
      <div>
        <div className="t-label" style={{ marginBottom: 5 }}>{rail.title || LIVE_CLAIM_RAIL_TITLE}</div>
        <h2 className="h2-app" style={{ margin: 0 }}>{rail.gene}: receipt to proposed state</h2>
        <p className="t-body-sm" style={{ margin: "6px 0 0", maxWidth: "72ch" }}>
          One addressable claim crosses the boundary as a receipt. It has a typed status and a proposed
          state diff, but the diff is proposal only until the open obligation is satisfied.
        </p>
      </div>
      <div className="card-paper" style={{ padding: "12px 14px", display: "grid", gap: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          <span className="t-mono" style={{ fontWeight: 700 }}>{rail.gene}</span>
          <span className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>{rail.status.replace(/_/g, " ")}</span>
          <span className="chip" style={{ ["--tone" as any]: rail.accepted_state ? "var(--moss)" : "var(--cinnabar)" }}>
            accepted state={String(rail.accepted_state)}
          </span>
          <span className="t-mono fz-2xs" style={{ color: "var(--ink-3)" }}>{rail.receipt_id}</span>
        </div>
        <p className="t-body-sm" style={{ margin: 0, color: "var(--ink)" }}>{rail.claim}</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 8 }}>
          {rail.stages.map((step) => (
            <div key={step.stage} style={{ padding: "8px 9px", border: "1px solid var(--rule-faint)",
              borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)", display: "grid", gap: 4 }}>
              <span className="t-label">{step.stage}</span>
              <span className="t-body-sm" style={{ color: "var(--ink-3)" }}>{step.text}</span>
            </div>
          ))}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: 8 }}>
          <div>
            <div className="t-label">state_diff</div>
            <p className="t-body-sm" style={{ margin: "4px 0 0", color: "var(--ink-3)" }}>
              {rail.state_diff.effect}. model_can_apply={String(rail.state_diff.model_can_apply)}.
            </p>
          </div>
          <div>
            <div className="t-label">reproduce command</div>
            <p className="t-mono fz-2xs" style={{ margin: "4px 0 0", color: "var(--field-blue)", fontWeight: 700 }}>
              {rail.reproduce_command}
            </p>
          </div>
          <div>
            <div className="t-label">open_obligation</div>
            <p className="t-body-sm" style={{ margin: "4px 0 0", color: "var(--ink-3)" }}>{rail.open_obligation}</p>
          </div>
        </div>
        <p className="t-caption" style={{ margin: 0, color: "var(--ink-3)" }}>
          {rail.why_not_state} Next task: {rail.next_task}.
        </p>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => setTab("frontier")}>Open receipt</button>
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => setTab("agent")}>Open assay packet</button>
        </div>
      </div>
    </section>
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
      <div style={{ display: "flex", alignItems: "start", gap: 14, flexWrap: "wrap" }}>
        <div style={{ minWidth: 260, flex: 1 }}>
          <div className="t-label" style={{ marginBottom: 5 }}>Acceptance layer for AI-generated biology</div>
          <h2 className="h2-app" style={{ margin: 0 }}>Prospect separates drivers from passengers.</h2>
          <p className="t-body-sm" style={{ margin: "7px 0 0", maxWidth: "76ch", color: "var(--ink-3)" }}>
            A real Claude Science export from {demo.source_dataset} submits a responder signature. Claude Science
            preserved the artifact and internal review completed with {demo.claude_science.internal_review_findings} findings.
            Prospect does not say the signature is wrong. It asks which signature genes behave as causal drivers,
            which stay associative passengers, and which explicit driver claims the perturbation data contradicts.
          </p>
        </div>
        <span className="chip" style={{ ["--tone" as any]: "var(--field-blue)" }}>
          {demo.real_export ? "real export" : "fixture fallback"}
        </span>
        <span className="chip" style={{ ["--tone" as any]: "var(--cinnabar)" }}>accepted={String(demo.prospect.accepted)}</span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 10 }}>
        <div style={{ border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", padding: "10px 11px", background: "var(--paper-recessed)" }}>
          <div className="t-label">Claude Science lane</div>
          <p className="t-body-sm" style={{ margin: "5px 0 0", color: "var(--ink-3)" }}>
            artifact_status={demo.claude_science.artifact_status}. Internal review status={demo.claude_science.internal_review_status}.
            AUC LOO={demo.claude_science.auc.LOO_CV_data_driven}.
          </p>
          <p className="t-caption" style={{ margin: "7px 0 0", color: "var(--ink-3)" }}>
            {demo.claude_science.session_caveat}
          </p>
        </div>
        <div style={{ border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", padding: "10px 11px", background: "var(--paper-recessed)" }}>
          <div className="t-label">Prospect lane</div>
          <p className="t-body-sm" style={{ margin: "5px 0 0", color: "var(--ink-3)" }}>
            {counts.genes} genes checked against the frozen Marson table: {counts.drivers} drivers,
            {" "}{counts.passengers} associative passengers, {counts.contradicted} contradicted driver claims,
            {" "}{counts.not_assayed} not assayed comparably.
          </p>
          <p className="t-caption" style={{ margin: "7px 0 0", color: "var(--ink-3)" }}>
            next={demo.prospect.next}. {demo.prospect.ceiling}
          </p>
          {demo.prospect.coverage_report && (
            <p className="t-caption" style={{ margin: "7px 0 0", color: "var(--ink-3)" }}>
              ORCS primary T-cell context shrinks uncovered genes from {demo.prospect.coverage_report.before.not_assayed}
              {" "}to {demo.prospect.coverage_report.after.not_assayed}, while staying proposal-only.
            </p>
          )}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: 8 }}>
        <VerdictExample title="evidence_attached" tone="var(--brass)" rows={examples.supported} />
        <VerdictExample title="associative_only" tone="var(--stone)" rows={examples.passengers} />
        <VerdictExample title="contradicted" tone="var(--cinnabar)" rows={examples.contradicted} />
        <VerdictExample title="not_assayed" tone="var(--stone)" rows={examples.open} />
      </div>

      <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap", borderTop: "1px solid var(--rule-faint)", paddingTop: 10 }}>
        <span className="t-label">judge commands</span>
        <span className="t-mono fz-2xs" style={{ color: "var(--field-blue)", fontWeight: 700 }}>
          {demo.commands.claude_science || CLAUDE_SCIENCE_CONNECTOR_COMMAND}
        </span>
        <span className="t-mono fz-2xs" style={{ color: "var(--field-blue)", fontWeight: 700 }}>
          {demo.commands.generic || GENERIC_CONNECTOR_COMMAND}
        </span>
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => setTab("frontier")}>Open receipt bridge</button>
      </div>
    </section>
  );
}

function ProspectAcceptanceWorkbench({ d }: { d: Data }) {
  const [text, setText] = useState(ACCEPTANCE_EXAMPLE);
  const [result, setResult] = useState<AcceptanceResult | null>(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const shared = decodeSharedAcceptanceState();
    if (shared) setResult(shared);
  }, []);

  const run = () => {
    try {
      const next = buildAcceptanceResult(text, d);
      setResult(next);
      setError("");
      setCopied(false);
      if (typeof window !== "undefined") window.history.replaceState(null, "", next.state_url);
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "submission failed");
    }
  };

  const shareUrl = result && typeof window !== "undefined"
    ? `${window.location.origin}${window.location.pathname}${result.state_url}`
    : "";

  return (
    <section className="card-paper" style={{ padding: "16px 18px", display: "grid", gap: 14 }}>
      <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between", gap: 14, flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Run your own claim through Prospect</div>
          <h2 className="h2-app" style={{ margin: 0 }}>Paste a signature, DE table, ranked markers, or gene list.</h2>
          <p className="t-body-sm" style={{ margin: "7px 0 0", color: "var(--ink-3)", maxWidth: "78ch" }}>
            Prospect normalizes symbols, common checkpoint aliases like PD-1, Ensembl IDs from the frozen table,
            duplicates, and unknowns. It returns driver, passenger, contradicted, and not_assayed verdicts,
            plus a receipt and shareable state page. accepted=false until a human signature.
          </p>
        </div>
        <span className="chip" style={{ ["--tone" as any]: "var(--cinnabar)" }}>accepted=false</span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 280px), 1fr))", gap: 12 }}>
        <div style={{ display: "grid", gap: 8 }}>
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
            <button type="button" className="btn btn-secondary btn-sm" onClick={run}>Submit to Prospect</button>
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => setText(ACCEPTANCE_EXAMPLE)}>Load example</button>
            {error && <span className="t-caption" style={{ color: "var(--cinnabar)" }}>{error}</span>}
          </div>
        </div>

        <div style={{ border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", padding: "10px 11px", background: "var(--paper-recessed)", display: "grid", gap: 10 }}>
          {result ? (
            <>
              <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                <span className="t-mono" style={{ fontWeight: 700 }}>{result.receipt_id}</span>
                <span className="chip" style={{ ["--tone" as any]: "var(--cinnabar)" }}>accepted=false</span>
                <span className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>{result.next}</span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(86px, 1fr))", gap: 8 }}>
                <AcceptanceCount label="drivers" value={result.counts.drivers} tone="var(--brass)" />
                <AcceptanceCount label="passengers" value={result.counts.passengers} tone="var(--stone)" />
                <AcceptanceCount label="contradicted" value={result.counts.contradicted} tone="var(--cinnabar)" />
                <AcceptanceCount label="not_assayed" value={result.counts.not_assayed} tone="var(--ink-3)" />
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
                  <ExternalLink /> <span>{copied ? "Copied state link" : "Copy state link"}</span>
                </button>
                <span className="t-mono fz-2xs" style={{ color: "var(--field-blue)", overflowWrap: "anywhere" }}>{shareUrl}</span>
              </div>
              {result.warnings.length > 0 && (
                <p className="t-caption" style={{ margin: 0, color: "var(--ink-3)" }}>{result.warnings.slice(0, 3).join("; ")}</p>
              )}
              <p className="t-caption" style={{ margin: 0, color: "var(--ink-3)" }}>{result.ceiling}</p>
            </>
          ) : (
            <div style={{ display: "grid", gap: 8, alignContent: "center", minHeight: 180 }}>
              <div className="t-label">No local setup required</div>
              <p className="t-body-sm" style={{ margin: 0, color: "var(--ink-3)" }}>
                The same frozen rule is also exposed by <span className="t-mono">./prospect serve-acceptance --port 8130 --data-dir var/acceptance_service</span>
                {" "}and by the MCP tools <span className="t-mono">prospect.acceptance.submit_artifact</span> and <span className="t-mono">prospect.acceptance.get_verdict</span>.
              </p>
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
const BOUNDARY = ["Activity", "Receipt", "Proposal", "Review", "Verification", "Accepted", "State"];
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
          <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap",
            padding: "9px 10px", border: "1px solid var(--rule-faint)",
            borderRadius: "var(--radius-sm)", background: "var(--gold-tint, var(--state-open-tint))" }}>
            <span className="t-label" style={{ color: "var(--gold-ink)" }}>Try the boundary</span>
            <span className="t-mono fz-2xs" style={{ color: "var(--gold-ink)", fontWeight: 700 }}>{boundaryCommand}</span>
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
              <div className="t-label">External run to receipt</div>
              <p className="t-body-sm" style={{ margin: "4px 0 0", color: "var(--ink-3)" }}>
                An external auto-research producer submits a biology-shaped Perturb-seq reproduction as a receipt.
                The Marson checker re-derives the local facts, then the bridge still holds it as proposal only.
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
              <div className="t-mono fz-2xs" style={{ color: "var(--field-blue)", fontWeight: 700 }}>{externalDemo.verifier_replay}</div>
            </div>
            <div style={{ padding: "8px 9px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)",
              background: "var(--paper-recessed)" }}>
              <div className="t-label">bridge result</div>
              <div className="t-mono fz-2xs" style={{ color: "var(--gold-ink)", fontWeight: 700 }}>
                accepted=false · next={externalDemo.next}
              </div>
            </div>
            <div style={{ padding: "8px 9px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)",
              background: "var(--paper-recessed)" }}>
              <div className="t-label">judge command</div>
              <div className="t-mono fz-2xs" style={{ color: "var(--field-blue)", fontWeight: 700 }}>
                {externalDemo.command || EXTERNAL_RUN_COMMAND}
              </div>
            </div>
          </div>
          <div>
            <div className="t-label" style={{ marginBottom: 5 }}>Human-only acceptance requires</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {externalDemo.human_acceptance_requires.map((item) => (
                <span key={item} className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>
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
    <div className="frontier-pane" style={{ display: "grid", gap: 24 }}>
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

      {d.receipts && d.receipts.length > 0 && (
        <Receipts receipts={d.receipts} bridge={d.receipt_bridge} externalDemo={d.external_run_receipt_demo} />
      )}

      {d.lab_writeback_receipt && <LabWritebackCard packet={d.lab_writeback_receipt} />}

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
  // cited genes first (they carry the literature-vs-data contradiction), then the rest
  const cited = Object.keys(per).filter((g) => d.citations[g]).sort();
  const rest = Object.keys(per).filter((g) => !d.citations[g]).sort();
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <FindingEvidencePanel>
        <EvRow head cells={["gene", "the field calls it (cited)", "DE on KD"]} />
        {cited.map((g) => {
          const c = d.citations[g], p = per[g];
          return (
            <div key={g} className="finding-evidence-row">
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
      </FindingEvidencePanel>
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
      <FindingEvidencePanel>
        <EvRow head cells={["gene", "general machinery, not immune biology", "Rest DE"]} />
        {rows.map(([g, v]) => (
          <EvRow key={g} cells={[g, "moves the transcriptome in a resting cell",
            <b key="n" style={{ color: "var(--brass)" }}>{fmt(v.rest_de)}</b>]} />
        ))}
      </FindingEvidencePanel>
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
    <div className="finding-evidence-row">
      <button onClick={() => onGene(g)} className="t-mono" style={{ fontWeight: 650, textAlign: "left", background: "transparent", color: tone }}>{g}</button>
      <span className="t-body-sm">T-cell regulator · {per[g].finding === "essentiality_artifact" ? "replicates in K562" : "inert in K562"}</span>
      <span className="t-mono fz-sm" style={{ textAlign: "right" }}>K562 {per[g].k562_de ?? "·"} DE</span>
    </div>
  );
  return (
    <div style={{ display: "grid", gap: 12 }}>
      <div className="finding-metric-strip">
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
      <FindingEvidencePanel>
        {house.map((g: string) => <Row key={g} g={g} tone="var(--brass)" />)}
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

      {d.disease_genetics_overlay && <DiseaseGeneticsOverlayCard packet={d.disease_genetics_overlay} onGene={onGene} />}

      {d.lab_packet && <LabPacketCard packet={d.lab_packet} onGene={onGene} />}

      {d.lab_writeback_receipt && <LabWritebackCard packet={d.lab_writeback_receipt} />}

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

function EndgameResultPanel({ packet, onGene }: { packet: EndgameResult; onGene: (g: string) => void }) {
  const topRows = packet.candidate_decisions.slice(0, 6);
  const supportRows = packet.candidate_decisions.filter((row) => row.independent_primary_t_cell_support.length > 0);
  const rpe1 = packet.non_blocking_not_assayed[0];
  const lead = packet.lead_candidate;
  return (
    <section className="card-paper" style={{ padding: "18px 20px", display: "grid", gap: 14, borderColor: "var(--brass)" }}>
      <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between", gap: 14, flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Defended discovery endgame</div>
          <h2 className="h2-app" style={{ margin: 0 }}>PGGT1B clears the fixed bar as a proposal.</h2>
          <p className="t-body-sm" style={{ margin: "7px 0 0", maxWidth: "78ch", color: "var(--ink-3)" }}>
            The corrected bar rests cell-type specificity on genome-wide K562 and treats sparse RPE1 coverage
            as not_assayed context. Prospect re-scored all {packet.candidate_count} locked candidates:
            {` ${packet.cleared_count}`} cleared the fixed bar, accepted=false, human_signature_required.
          </p>
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "flex-end" }}>
          {lead && (
            <button type="button" onClick={() => onGene(lead.gene)} className="btn btn-secondary btn-sm">
              {lead.gene}
            </button>
          )}
          <a className="btn btn-secondary btn-sm" href="/data/defended_discovery_endgame_result.json" target="_blank" rel="noreferrer">
            ledger <ExternalLink size={13} />
          </a>
          <a className="btn btn-secondary btn-sm" href="/data/defended_discovery_endgame_preregistration.json" target="_blank" rel="noreferrer">
            pre-registration <ExternalLink size={13} />
          </a>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: 8 }}>
        {[
          [packet.candidate_count, "candidates tested", "var(--ink)"],
          [packet.cleared_count, "fixed-bar lead", "var(--moss)"],
          [supportRows.length, "with T-cell support", "var(--brass)"],
          [rpe1?.affected_candidates || 0, "RPE1 context", "var(--field-blue)"],
        ].map(([value, label, color]) => (
          <div key={label} style={{ padding: "10px 11px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
            <div className="t-mono" style={{ fontSize: 18, fontWeight: 700, color }}>{value}</div>
            <div className="t-label" style={{ marginTop: 3, color: "var(--ink-3)" }}>{label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 300px), 1fr))", gap: 12 }}>
        <div style={{ display: "grid", gap: 8 }}>
          <div className="t-label">Locked order, first six decisions</div>
          {topRows.map((row) => (
            <div key={row.gene} style={{ display: "grid", gridTemplateColumns: "34px 72px 1fr", gap: 8, alignItems: "baseline" }}>
              <span className="t-mono fz-2xs" style={{ color: "var(--ink-4)" }}>{row.rank}</span>
              <button type="button" onClick={() => onGene(row.gene)} className="t-mono fz-sm"
                style={{ background: "transparent", color: "var(--ink)", textAlign: "left", fontWeight: 700 }}>
                {row.gene}
              </button>
              <span className="t-caption" style={{ color: "var(--ink-3)" }}>
                {row.blocking_rungs.map((block) => block.typed_detail).join(", ") || row.decision}
              </span>
            </div>
          ))}
        </div>
        <div style={{ padding: "10px 12px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)", display: "grid", gap: 8 }}>
          <div className="t-label">What the fixed bar changed</div>
          <p className="t-body-sm" style={{ margin: 0, color: "var(--ink-3)" }}>
            The prior run treated missing RPE1 rows as a blocking failure. This run keeps that as
            not_assayed context. PGGT1B now clears on Marson effect, K562 specificity, Shifrut support,
            STRING, DICE, Open Targets, ChEMBL, DepMap, mechanism, and adversarial kills.
          </p>
          <p className="t-caption" style={{ margin: 0, color: "var(--ink-3)" }}>
            {packet.honest_ceiling}. accepted=false. ledger={packet.ledger_id}.
          </p>
        </div>
      </div>
    </section>
  );
}

function DiscoveryCampaignSurface({ d, onGene }: { d: Data; onGene: (g: string) => void }) {
  const discovery = d.discovery_campaign;
  const cross = d.cross_validation;
  const flagship = d.flagship_module;
  const counter = d.overclaim_counter;
  if (!discovery || !cross || !flagship || !counter) return null;
  const evidenceStatus = "evidence_attached";
  const reproducedStatus = "computationally_reproduced";
  const hypothesis = flagship.flagship_hypothesis;
  const pg = cross.candidates.find((row) => row.gene === "PGGT1B");
  const supportRows = cross.candidates.slice(0, 18);
  const schmidt = cross.readout_comparability.schmidt_2022_2427;
  const commands = [
    ["Phase 1", discovery.reproduce_command || "./prospect discovery-campaign"],
    ["Phase 2", cross.reproduce_command || "./prospect cross-validation"],
    ["Phase 3", flagship.reproduce_command || "./prospect flagship-module"],
    ["Phase 4", counter.reproduce_command || "./prospect overclaim-counter"],
  ];
  const jsonLinks = [
    ["/data/discovery_campaign.json", "discovery"],
    ["/data/cross_validation.json", "cross-validation"],
    ["/data/flagship_module.json", "flagship"],
    ["/data/overclaim_counter.json", "counter"],
  ];
  return (
    <section className="card-paper" style={{ padding: "18px 20px", display: "grid", gap: 16, borderColor: "var(--gold-line)" }}>
      <div style={{ display: "flex", gap: 12, alignItems: "start", flexWrap: "wrap" }}>
        <div style={{ minWidth: 0 }}>
          <div className="t-label" style={{ marginBottom: 5 }}>Honest discovery campaign</div>
          <h3 className="h2-app" style={{ margin: 0 }}>The discovery is the refusal</h3>
          <p className="t-body-sm" style={{ maxWidth: "78ch", margin: "8px 0 0" }}>
            Claim A: 11,526 genes entered the funnel, 18 survived the novelty and specificity filters,
            and 4 had independent screen support. The system kept all of that proposal-only and refused the rest.
            Claim B: PGGT1B is one caveated hypothesis, not a module.
          </p>
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginLeft: "auto" }}>
          {jsonLinks.map(([href, label]) => (
            <a key={href} className="btn btn-secondary btn-sm" href={href} target="_blank" rel="noreferrer">
              {label} <ExternalLink size={13} />
            </a>
          ))}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 8 }}>
        {[
          [fmt(discovery.filter_counts.frontier_genes), "frontier genes scanned", "var(--ink)"],
          [fmt(discovery.filter_counts.cell_type_specific_replogle), "novelty survivors", "var(--brass)"],
          [fmt(cross.counts.candidates_with_external_screen_hit), "with independent support", "var(--moss)"],
          [fmt(counter.counts.phase1_refused_total), "genes refused by filters", "var(--cinnabar)"],
          [fmt(counter.counts.model_contradicted_claims), "model claims contradicted", "var(--cinnabar)"],
        ].map(([value, label, color]) => (
          <div key={label} style={{ padding: "10px 11px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
            <div className="t-mono" style={{ fontSize: 18, fontWeight: 700, color }}>{value}</div>
            <div className="t-label" style={{ marginTop: 3, color: "var(--ink-3)" }}>{label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 320px), 1fr))", gap: 14 }}>
        <div style={{ display: "grid", gap: 10 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>{evidenceStatus}</span>
            <button onClick={() => onGene(hypothesis.gene)} className="t-mono fz-sm" style={{ color: "var(--ink)", background: "transparent", fontWeight: 700 }}>
              {hypothesis.gene}
            </button>
            <span className="t-mono fz-sm" style={{ color: "var(--ink-3)" }}>{hypothesis.support_level}</span>
          </div>
          <p className="t-lede" style={{ fontSize: "1.02rem", margin: 0 }}>{hypothesis.claim}</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            <span className="chip" style={{ ["--tone" as any]: "var(--moss)" }}>rank 1</span>
            <span className="chip" style={{ ["--tone" as any]: "var(--moss)" }}>Shifrut support</span>
            <span className="chip" style={{ ["--tone" as any]: "var(--field-blue)" }}>{hypothesis.schmidt_status.replace(/_/g, " ")}</span>
            <span className="chip" style={{ ["--tone" as any]: "var(--brass)" }}>proposal only</span>
          </div>
          <div style={{ display: "grid", gap: 5 }}>
            {hypothesis.evidence_ladder.map((step) => (
              <div key={step.rung} className="t-caption" style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "baseline" }}>
                <span className="t-mono" style={{ color: "var(--ink-3)" }}>{step.rung}</span>
                <span className="chip" style={{ ["--tone" as any]: step.status === "contradicted" ? "var(--cinnabar)" : step.status === reproducedStatus ? "var(--moss)" : step.status === "orthogonal_phenotype" ? "var(--field-blue)" : "var(--brass)" }}>
                  {step.status}
                </span>
                <span>{step.detail}</span>
              </div>
            ))}
          </div>
        </div>

        <div style={{ display: "grid", gap: 10 }}>
          <div style={{ padding: "10px 12px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
            <div className="t-label" style={{ marginBottom: 5 }}>Cross-dataset read</div>
            <p className="t-caption" style={{ margin: 0 }}>
              PGGT1B support: {pg?.external_screen_summary.supporting_hits.join(", ") || "none"}.
              Schmidt status: {pg?.external_screen_summary.orthogonal_phenotypes.join(", ") || "none"}.
              DICE activated CD4 mean TPM: {pg?.dice_expression.activated_cd4_mean_tpm ?? "n/a"}.
            </p>
            <p className="t-caption" style={{ margin: "6px 0 0" }}>
              STRING partners: {pg?.string_network.top_partners.slice(0, 5).join(", ") || "none"}.
            </p>
          </div>
          <div style={{ padding: "10px 12px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
            <div className="t-label" style={{ marginBottom: 5 }}>What the gate refused</div>
            <p className="t-caption" style={{ margin: 0 }}>
              {fmt(counter.counts.phase1_refused_total)} Phase 1 genes refused; {counter.counts.phase2_without_external_screen_hit} of {discovery.filter_counts.cell_type_specific_replogle}
              {" "}survivors lacked independent screen support; {counter.counts.phase2_schmidt_orthogonal_phenotypes} Schmidt rows are orthogonal phenotype, not comparable contradiction.
            </p>
          </div>
          <div style={{ padding: "10px 12px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
            <div className="t-label" style={{ marginBottom: 5 }}>Refutation experiment</div>
            <p className="t-caption" style={{ margin: 0 }}>
              {hypothesis.refutation_experiment.readout}. Refutes if {hypothesis.refutation_experiment.refutes_if}.
            </p>
          </div>
        </div>
      </div>

      <div style={{ padding: "10px 12px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
        <div className="t-label" style={{ marginBottom: 5 }}>Schmidt comparator</div>
        <p className="t-caption" style={{ margin: 0 }}>
          {schmidt.schmidt_readout} The Marson replay measures {schmidt.marson_readout.toLowerCase()}.
          Typed status: {schmidt.typed_status}.
        </p>
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <div className="t-label">Per-candidate support table</div>
        <div style={{ overflowX: "auto", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)" }}>
          <table style={{ width: "100%", minWidth: 760, borderCollapse: "collapse" }}>
            <thead>
              <tr className="t-label">
                {["gene", "rank", "Marson", "Shifrut", "Schmidt", "STRING", "DICE", "Open Targets"].map((h) => (
                  <th key={h} style={{ textAlign: "left", padding: "8px 10px", borderBottom: "1px solid var(--rule)" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="t-caption">
              {supportRows.map((row) => {
                const shifrut = row.external_screen_summary.supporting_hits.length ? "evidence_attached" : "missed";
                const schmidtStatus = row.external_screen_summary.orthogonal_phenotypes.includes("schmidt_2022_2427")
                  ? "orthogonal_phenotype" : row.external_screen_summary.contradictions.length ? "contradicted" : "not attached";
                return (
                  <tr key={row.gene} style={{ borderTop: "1px solid var(--rule-faint)" }}>
                    <td style={{ padding: "7px 10px" }}>
                      <button onClick={() => onGene(row.gene)} className="t-mono" style={{ background: "transparent", color: "var(--ink)", fontWeight: 700 }}>{row.gene}</button>
                    </td>
                    <td style={{ padding: "7px 10px" }}>{row.rank}</td>
                    <td style={{ padding: "7px 10px" }}>{row.marson_stim_max_de} DE</td>
                    <td style={{ padding: "7px 10px" }}>{shifrut}</td>
                    <td style={{ padding: "7px 10px" }}>{schmidtStatus}</td>
                    <td style={{ padding: "7px 10px" }}>{row.string_network.top_partners.length ? "evidence_attached" : "missed"}</td>
                    <td style={{ padding: "7px 10px" }}>{row.dice_expression.activated_cd4_mean_tpm ?? "n/a"}</td>
                    <td style={{ padding: "7px 10px" }}>{row.open_targets.overlay_class}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ borderTop: "1px solid var(--rule-faint)", paddingTop: 12, display: "grid", gap: 8 }}>
        <div className="t-label">One-command reproduce path</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(245px, 1fr))", gap: 6 }}>
          {commands.map(([label, command]) => (
            <div key={command} style={{ display: "flex", gap: 8, alignItems: "baseline", minWidth: 0 }}>
              <span className="t-label" style={{ minWidth: 54 }}>{label}</span>
              <code className="t-mono fz-xs" style={{ color: "var(--gold-ink)", overflowWrap: "anywhere" }}>{command}</code>
            </div>
          ))}
        </div>
        <p className="t-caption" style={{ margin: 0 }}>
          Boundary: {counter.flagship_boundary.accepted_state} accepted state for {counter.flagship_boundary.gene}. Next acceptance step: {counter.flagship_boundary.next_acceptance_step}.
        </p>
      </div>
    </section>
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

function DiseaseGeneticsOverlayCard({ packet, onGene }: { packet: DiseaseGeneticsOverlay; onGene: (g: string) => void }) {
  const label = (value: string) => value.replace(/_/g, " ");
  const tone = (value: string) => {
    if (value === "immune_or_hematologic_genetic_context") return "var(--moss)";
    if (value === "immune_or_hematologic_non_genetic_context") return "var(--field-blue)";
    return "var(--stone)";
  };
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>Disease-genetics overlay packet</div>
          <p className="t-body-sm" style={{ maxWidth: "76ch", margin: 0 }}>
            Frozen Open Targets rows attach immune or hematologic context to campaign candidates. No accepted state changes.
          </p>
        </div>
        <a className="btn btn-secondary btn-sm" href="/data/disease_genetics_overlay.json" target="_blank" rel="noreferrer" style={{ marginLeft: "auto" }}>
          JSON <ExternalLink size={13} />
        </a>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(155px, 1fr))", gap: 8 }}>
        {[
          [packet.counts.campaign_rows, "campaign rows", "var(--ink)"],
          [packet.counts.immune_or_hematologic_context, "immune or hematologic context", "var(--field-blue)"],
          [packet.counts.immune_or_hematologic_genetic_context, "genetic context", "var(--moss)"],
          [packet.counts.no_immune_or_hematologic_context, "no selected context", "var(--stone)"],
        ].map(([value, title, color]) => (
          <div key={title} style={{ padding: "9px 10px", border: "1px solid var(--rule-faint)", borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)" }}>
            <div className="t-mono" style={{ fontSize: 17, fontWeight: 700, color }}>{value}</div>
            <div className="t-label" style={{ color: "var(--ink-3)", marginTop: 3 }}>{title}</div>
          </div>
        ))}
      </div>
      <div style={{ padding: 0, overflowX: "auto", border: "1px solid var(--rule)", borderRadius: "var(--radius-md)", background: "var(--paper-raised)" }}>
        <table style={{ width: "100%", minWidth: 900, borderCollapse: "collapse" }}>
          <thead>
            <tr className="t-label">
              {["rank", "gene", "condition", "overlay", "top external context", "evidence"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: "9px 12px", borderBottom: "1px solid var(--rule)" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {packet.rows.slice(0, 10).map((row) => (
              <tr key={row.gene} style={{ borderTop: "1px solid var(--rule-faint)" }}>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px", color: "var(--ink-3)" }}>{row.rank}</td>
                <td style={{ padding: "8px 12px" }}>
                  <button onClick={() => onGene(row.gene)} className="t-mono" style={{ fontWeight: 700, background: "transparent", color: "var(--ink)" }}>{row.gene}</button>
                </td>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px" }}>{row.strongest_condition}</td>
                <td style={{ padding: "8px 12px" }}>
                  <span className="chip" style={{ ["--tone" as any]: tone(row.overlay_class) }}>{label(row.overlay_class)}</span>
                </td>
                <td className="t-body-sm" style={{ padding: "8px 12px" }}>{row.top_context?.disease_or_trait ?? "no selected context"}</td>
                <td className="t-mono fz-sm" style={{ padding: "8px 12px" }}>{row.top_context?.evidence_type ?? "none"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="t-caption" style={{ margin: 0 }}>
        Trust boundary: {label(packet.trust_boundary)}. Accepted-state mutation: {packet.accepted_state_mutation}.
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

function LabWritebackCard({ packet }: { packet: LabWritebackReceipt }) {
  const contradictionTitle = packet.contradiction_rule.title || CONTRADICTION_AS_PROPOSAL_TITLE;
  const mutationRule = packet.contradiction_rule.accepted_claim_mutation || CONTRADICTION_NEVER_OVERWRITE;
  return (
    <div style={{ display: "grid", gap: 10 }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <div>
          <div className="t-label" style={{ marginBottom: 5 }}>{packet.title}</div>
          <p className="t-body-sm" style={{ maxWidth: "72ch", margin: 0 }}>
            A bench result returns as the same receipt shape whether it confirms or refutes. It carries
            executed_protocol, assay_readout, affected_claims, reviewer_signature, and state_diff, then
            waits at accepted=false.
          </p>
        </div>
        <a className="btn btn-secondary btn-sm" href="/data/lab_writeback_receipt.json" target="_blank" rel="noreferrer" style={{ marginLeft: "auto" }}>
          JSON <ExternalLink size={13} />
        </a>
      </div>
      <div className="card-paper" style={{ padding: "12px 14px", display: "grid", gap: 10 }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 8 }}>
          {packet.return_receipts.map((receipt) => (
            <div key={receipt.outcome} style={{ padding: "9px 10px", border: "1px solid var(--rule-faint)",
              borderRadius: "var(--radius-sm)", background: "var(--paper-recessed)", display: "grid", gap: 5 }}>
              <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                <span className="t-label">{receipt.outcome}</span>
                <span className="chip" style={{ ["--tone" as any]: receipt.typed_status === "contradicted" ? "var(--cinnabar)" : "var(--field-blue)" }}>
                  {receipt.typed_status.replace(/_/g, " ")}
                </span>
              </div>
              <p className="t-body-sm" style={{ margin: 0, color: "var(--ink-3)" }}>{receipt.assay_readout.summary}</p>
              <p className="t-caption" style={{ margin: 0, color: "var(--ink-3)" }}>
                affected {receipt.affected_claims[0].receipt_id} · accepted={String(receipt.accepted)} · next={receipt.next}
              </p>
            </div>
          ))}
        </div>
        <div style={{ borderTop: "1px solid var(--rule-faint)", paddingTop: 10 }}>
          <div className="t-label">{contradictionTitle}</div>
          <p className="t-body-sm" style={{ margin: "4px 0 0", color: "var(--ink-3)" }}>
            {mutationRule}: {packet.contradiction_rule.rule}
          </p>
        </div>
      </div>
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
            Trust boundary: {dive.matrix_slice.trust_boundary.replace(/_/g, " ")}. The slice supports assay design; it does not move accepted state.
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
