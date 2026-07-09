"""Run the pre-registered overnight compute program."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontier import predicates as P
from receipt.input_normalizer import ALIASES

DATA = ROOT / "examples" / "data"
OUT = ROOT / "output"
LOG = OUT / "overnight_compute.log"

PREREG_JSON = DATA / "overnight_preregistration.json"
MARSON_FULL = DATA / "marson_de_full.csv"
REPLOGLE_K562 = DATA / "replogle_k562_de.csv"
REPLOGLE_RPE1 = DATA / "replogle_rpe1_de.csv"
COLLECTRI = DATA / "collectri_human.csv"
CROSS_VALIDATION_SOURCES = DATA / "cross_validation_sources.json"
DISEASE_OVERLAY = DATA / "disease_genetics_overlay.json"

ATLAS_JSON = DATA / "overnight_genome_wide_atlas.json"
ATLAS_CSV = DATA / "overnight_genome_wide_atlas.csv"
LITERATURE_CLAIMS_JSON = DATA / "overnight_literature_claims.json"
LITERATURE_AUDIT_JSON = DATA / "overnight_literature_audit.json"
LITERATURE_AUDIT_CSV = DATA / "overnight_literature_audit.csv"
LEADERBOARD_JSON = DATA / "overnight_defended_leaderboard.json"
LEADERBOARD_CSV = DATA / "overnight_defended_leaderboard.csv"
REPORT_DOC = ROOT / "docs" / "OVERNIGHT_COMPUTE_REPORT.md"

HONEST_CEILING = "Computation over released data, not wet-lab or clinical truth."
CONDITIONS = ["Rest", "Stim8hr", "Stim48hr"]
DRIVER_DE_THRESHOLD = 10
K562_SPECIFICITY_WARNING_DE = 25
MAX_LITERATURE_RECORDS_PER_QUERY = 100
EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

DRIVER_WORDS = [
    "regulates",
    "regulator",
    "regulatory",
    "drives",
    "controls",
    "required",
    "essential",
    "mediates",
    "promotes",
    "inhibits",
]
CD4_CONTEXT_RE = re.compile(r"\b(CD4|T cell|T-cell|T lymphocyte|helper T|TCR)\b", re.I)
COMPARABLE_RE = re.compile(r"\b(activation|activate|activated|TCR|transcription|transcriptome|state|proliferation|differentiation)\b", re.I)
ORTHOGONAL_RE = re.compile(r"\b(cytokine|exhaustion|exhausted|checkpoint|disease|immunotherapy|response|survival|tumou?r|cancer|autoimmune)\b", re.I)
CD4_CONTEXT_ONLY_RE = re.compile(r"\bCD4\s*(\+|-positive|positive)?\s*(T[-\s]?cell|cell|target cells?)", re.I)


def _log(message: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with LOG.open("a") as fh:
        fh.write(f"{stamp} {message}\n")
    print(message)


def _load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"missing required source: {path}")
    return json.loads(path.read_text())


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_obj(prefix: str, obj: Any) -> str:
    digest = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"{prefix}_{digest[:16]}"


def _load_simple_de(path: Path, field: str) -> dict[str, int]:
    if not path.exists():
        return {}
    with path.open(newline="") as fh:
        return {row["gene"]: int(row[field]) for row in csv.DictReader(fh)}


def _load_collectri_counts() -> dict[str, int]:
    counts: dict[str, int] = Counter()
    with COLLECTRI.open(newline="") as fh:
        for row in csv.DictReader(fh):
            counts[row["tf"]] += 1
    return dict(counts)


def _load_marson() -> dict[str, dict[str, Any]]:
    genes: dict[str, dict[str, Any]] = defaultdict(lambda: {"conditions": {}})
    with MARSON_FULL.open(newline="") as fh:
        for row in csv.DictReader(fh):
            gene = row["target_contrast_gene_name"]
            cond = row["culture_condition"]
            genes[gene]["gene"] = gene
            genes[gene]["ensembl_id"] = row["target_contrast"].split(".", 1)[0]
            genes[gene]["conditions"][cond] = {
                "condition": cond,
                "n_total_de_genes": int(row["n_total_de_genes"]),
                "n_up_genes": int(row["n_up_genes"]),
                "n_down_genes": int(row["n_down_genes"]),
                "ontarget_effect_size": float(row["ontarget_effect_size"]),
                "ontarget_significant": row["ontarget_significant"] == "True",
                "offtarget_flag": row["offtarget_flag"] == "True",
                "ontarget_effect_category": row["ontarget_effect_category"],
                "n_downstream": int(row["n_downstream"]),
            }
    return dict(genes)


def _best_on_target(row: dict[str, Any]) -> dict[str, Any] | None:
    candidates = [
        cond
        for cond in row["conditions"].values()
        if cond["ontarget_effect_category"] == "on-target KD"
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda item: int(item["n_total_de_genes"]))


def _atlas_status(best: dict[str, Any] | None) -> str:
    if best is None:
        return "not_assayed"
    if int(best["n_total_de_genes"]) > DRIVER_DE_THRESHOLD:
        return "evidence_attached"
    return "associative_only"


def build_genome_wide_atlas() -> dict[str, Any]:
    prereg = _load_json(PREREG_JSON)
    _log("phase1 start genome-wide atlas")
    marson = _load_marson()
    k562 = _load_simple_de(REPLOGLE_K562, "k562_de")
    rpe1 = _load_simple_de(REPLOGLE_RPE1, "rpe1_de")
    collectri = _load_collectri_counts()
    cross_sources = _load_json(CROSS_VALIDATION_SOURCES)
    disease = _load_json(DISEASE_OVERLAY)
    disease_by_gene = {row["gene"]: row for row in disease.get("rows", [])}
    screen_rows = cross_sources.get("screen_rows", {})
    string_network = cross_sources.get("string_network", {})
    dice_expression = cross_sources.get("dice_expression", {})

    rows: list[dict[str, Any]] = []
    for index, gene in enumerate(sorted(marson), start=1):
        source = marson[gene]
        best = _best_on_target(source)
        status = _atlas_status(best)
        conditions = source["conditions"]
        rest_de = int(conditions.get("Rest", {}).get("n_total_de_genes", 0))
        stim8 = int(conditions.get("Stim8hr", {}).get("n_total_de_genes", 0))
        stim48 = int(conditions.get("Stim48hr", {}).get("n_total_de_genes", 0))
        k562_de = k562.get(gene)
        rpe1_de = rpe1.get(gene)
        cross_refs = {
            "k562": "covered" if k562_de is not None else "not_assayed",
            "rpe1": "covered" if rpe1_de is not None else "not_assayed",
            "shifrut_orcs": "covered" if gene in screen_rows else "not_assayed",
            "schmidt_orcs": "orthogonal_phenotype" if gene in screen_rows else "not_assayed",
            "string": "covered" if gene in string_network else "not_assayed",
            "dice": "covered" if gene in dice_expression else "not_assayed",
            "open_targets": "covered" if gene in disease_by_gene else "not_assayed",
        }
        specificity = "not_assayed"
        if k562_de is not None:
            specificity = "specificity_warning" if k562_de > K562_SPECIFICITY_WARNING_DE else "cell_type_specific_context"
        row = {
            "rank": index,
            "gene": gene,
            "ensembl_id": source["ensembl_id"],
            "typed_status": status,
            "accepted": False,
            "next": "human_signature_required",
            "strongest_condition": best["condition"] if best else "",
            "strongest_n_total_de_genes": int(best["n_total_de_genes"]) if best else None,
            "strongest_n_up_genes": int(best["n_up_genes"]) if best else None,
            "strongest_n_down_genes": int(best["n_down_genes"]) if best else None,
            "strongest_effect_size": float(best["ontarget_effect_size"]) if best else None,
            "strongest_offtarget_flag": bool(best["offtarget_flag"]) if best else None,
            "rest_de": rest_de,
            "stim8hr_de": stim8,
            "stim48hr_de": stim48,
            "k562_de": k562_de,
            "rpe1_de": rpe1_de,
            "specificity_status": specificity,
            "collectri_target_count": int(collectri.get(gene, 0)),
            "standard_t_cell_annotation": gene in P.CANON,
            "cross_dataset_coverage": cross_refs,
            "honest_ceiling": HONEST_CEILING,
        }
        rows.append(row)
        if index % 1000 == 0:
            _log(f"phase1 checkpoint scored {index} genes")

    counts = Counter(row["typed_status"] for row in rows)
    packet = {
        "phase": "overnight_phase_1_genome_wide_atlas",
        "pre_registration_id": prereg["pre_registration_id"],
        "frontier_root": prereg["frontier_root"],
        "accepted": False,
        "next": "human_signature_required",
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "gene_count": len(rows),
        "typed_status_counts": dict(counts),
        "specificity_warning_count": sum(1 for row in rows if row["specificity_status"] == "specificity_warning"),
        "source_hashes": {
            "marson_de_full": _sha256(MARSON_FULL),
            "replogle_k562": _sha256(REPLOGLE_K562),
            "replogle_rpe1": _sha256(REPLOGLE_RPE1),
            "collectri": _sha256(COLLECTRI),
            "cross_validation_sources": _sha256(CROSS_VALIDATION_SOURCES),
            "disease_overlay": _sha256(DISEASE_OVERLAY),
        },
        "rows": rows,
        "reproduce_command": "./prospect overnight-compute --phase atlas",
    }
    packet["atlas_id"] = _hash_obj("overnight_atlas", packet)
    packet["content_signature"] = {
        "type": "sha256_content_hash_not_human_acceptance",
        "sha256": hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    }
    ATLAS_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    with ATLAS_CSV.open("w", newline="") as fh:
        fields = [
            "rank", "gene", "typed_status", "strongest_condition", "strongest_n_total_de_genes",
            "rest_de", "stim8hr_de", "stim48hr_de", "k562_de", "rpe1_de",
            "specificity_status", "collectri_target_count", "standard_t_cell_annotation",
        ]
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})
    _log(f"phase1 complete genes={len(rows)} evidence_attached={counts.get('evidence_attached', 0)} associative_only={counts.get('associative_only', 0)} not_assayed={counts.get('not_assayed', 0)}")
    return packet


def _gene_regex(symbols: set[str]) -> re.Pattern[str]:
    extraction_symbols = symbols - {"CD4"}
    tokens = sorted((re.escape(symbol) for symbol in extraction_symbols if len(symbol) >= 3), key=len, reverse=True)
    return re.compile(r"\b(" + "|".join(tokens) + r")\b")


def _driver_word_present(text: str) -> bool:
    lower = text.lower()
    return any(word in lower for word in DRIVER_WORDS)


def _sentence_split(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text or "") if part.strip()]


def _clean_claim_text(text: str) -> str:
    without_tags = re.sub(r"<[^>]+>", "", text or "")
    return " ".join(html.unescape(without_tags).replace("\u207a", "+").split())


def _fetch_europe_pmc(query: str, page_size: int) -> list[dict[str, Any]]:
    params = {
        "query": query,
        "format": "json",
        "pageSize": str(page_size),
        "resultType": "core",
    }
    url = EUROPE_PMC + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "prospect-hackathon/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = json.loads(response.read().decode())
    return body.get("resultList", {}).get("result", [])


def _claim_comparability(sentence: str, full_text: str) -> str:
    basis = sentence + " " + full_text
    if COMPARABLE_RE.search(basis) and not ORTHOGONAL_RE.search(sentence):
        return "comparable"
    return "orthogonal_phenotype"


def _literature_status(atlas_by_gene: dict[str, dict[str, Any]], gene: str, comparability: str) -> str:
    if comparability != "comparable":
        return "orthogonal_phenotype"
    row = atlas_by_gene.get(gene)
    if not row:
        return "not_assayed"
    if row["typed_status"] == "evidence_attached":
        return "evidence_attached"
    if row["typed_status"] == "associative_only":
        return "contradicted"
    return "not_assayed"


def build_literature_audit() -> dict[str, Any]:
    prereg = _load_json(PREREG_JSON)
    atlas = _load_json(ATLAS_JSON) if ATLAS_JSON.exists() else build_genome_wide_atlas()
    atlas_by_gene = {row["gene"]: row for row in atlas["rows"]}
    symbols = set(atlas_by_gene)
    aliases = {key: value for key, value in ALIASES.items() if value in symbols}
    search_symbols = symbols | set(aliases)
    gene_re = _gene_regex(search_symbols)
    query_plan = prereg["phase_2_literature_audit_rules"]["query_plan"]
    _log("phase2 start literature audit")

    raw_docs: dict[str, dict[str, Any]] = {}
    claims: dict[tuple[str, str, str], dict[str, Any]] = {}
    for query_index, query in enumerate(query_plan, start=1):
        try:
            docs = _fetch_europe_pmc(query, MAX_LITERATURE_RECORDS_PER_QUERY)
        except Exception as exc:
            _log(f"phase2 fetch failed query={query!r} error={exc}")
            docs = []
        _log(f"phase2 fetched query {query_index}/{len(query_plan)} records={len(docs)}")
        for doc in docs:
            pmid = str(doc.get("pmid") or doc.get("id") or "")
            if not pmid:
                continue
            title = doc.get("title") or ""
            abstract = doc.get("abstractText") or ""
            full_text = _clean_claim_text(f"{title}. {abstract}")
            if not CD4_CONTEXT_RE.search(full_text):
                continue
            raw_docs[pmid] = {
                "pmid": pmid,
                "title": title,
                "journal": doc.get("journalTitle", ""),
                "pub_year": doc.get("pubYear", ""),
                "doi": doc.get("doi", ""),
                "query": query,
                "abstract": abstract,
            }
            for sentence in _sentence_split(full_text):
                clean_sentence = _clean_claim_text(sentence)
                if not _driver_word_present(clean_sentence):
                    continue
                for match in gene_re.finditer(clean_sentence):
                    submitted = match.group(1)
                    gene = aliases.get(submitted, submitted)
                    if gene == "CD4" and CD4_CONTEXT_ONLY_RE.search(clean_sentence):
                        continue
                    if gene not in atlas_by_gene:
                        continue
                    comparability = _claim_comparability(clean_sentence, full_text)
                    status = _literature_status(atlas_by_gene, gene, comparability)
                    key = (pmid, gene, clean_sentence)
                    claims[key] = {
                        "pmid": pmid,
                        "gene": gene,
                        "matched_token": submitted,
                        "typed_status": status,
                        "readout_comparability": comparability,
                        "claim_sentence": clean_sentence,
                        "title": title,
                        "journal": doc.get("journalTitle", ""),
                        "pub_year": doc.get("pubYear", ""),
                        "doi": doc.get("doi", ""),
                        "marson_strongest_de": atlas_by_gene[gene]["strongest_n_total_de_genes"],
                        "marson_strongest_condition": atlas_by_gene[gene]["strongest_condition"],
                        "reason": _literature_reason(atlas_by_gene[gene], status, comparability),
                    }
        time.sleep(float(prereg["phase_2_literature_audit_rules"]["rate_limit_seconds"]))

    claim_rows = sorted(claims.values(), key=lambda row: (row["pmid"], row["gene"], row["claim_sentence"]))
    counts = Counter(row["typed_status"] for row in claim_rows)
    corpus = {
        "phase": "overnight_literature_claim_corpus",
        "pre_registration_id": prereg["pre_registration_id"],
        "accepted": False,
        "source": "Europe PMC open API",
        "query_plan": query_plan,
        "document_count": len(raw_docs),
        "claim_count": len(claim_rows),
        "documents": sorted(raw_docs.values(), key=lambda row: row["pmid"]),
        "claims": claim_rows,
    }
    corpus["corpus_id"] = _hash_obj("overnight_literature_corpus", corpus)
    LITERATURE_CLAIMS_JSON.write_text(json.dumps(corpus, indent=2, sort_keys=True) + "\n")
    packet = {
        "phase": "overnight_phase_2_literature_contradiction_audit",
        "pre_registration_id": prereg["pre_registration_id"],
        "frontier_root": prereg["frontier_root"],
        "accepted": False,
        "next": "human_signature_required",
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "corpus_id": corpus["corpus_id"],
        "document_count": len(raw_docs),
        "claim_count": len(claim_rows),
        "typed_status_counts": dict(counts),
        "contradiction_rate": round(counts.get("contradicted", 0) / len(claim_rows), 4) if claim_rows else 0,
        "claims": claim_rows,
        "reproduce_command": "./prospect overnight-compute --phase literature",
    }
    packet["audit_id"] = _hash_obj("overnight_literature_audit", packet)
    LITERATURE_AUDIT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    with LITERATURE_AUDIT_CSV.open("w", newline="") as fh:
        fields = ["pmid", "gene", "typed_status", "readout_comparability", "marson_strongest_de", "marson_strongest_condition", "title", "claim_sentence"]
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in claim_rows:
            writer.writerow({field: row.get(field) for field in fields})
    _log(f"phase2 complete docs={len(raw_docs)} claims={len(claim_rows)} contradicted={counts.get('contradicted', 0)} evidence_attached={counts.get('evidence_attached', 0)} orthogonal={counts.get('orthogonal_phenotype', 0)}")
    return packet


def _literature_reason(atlas_row: dict[str, Any], status: str, comparability: str) -> str:
    if comparability != "comparable":
        return "The sentence does not make a comparable activation-transcriptome driver claim, so it is retained as orthogonal_phenotype."
    if status == "evidence_attached":
        return f"Comparable driver claim; Marson on-target perturbation moves {atlas_row['strongest_n_total_de_genes']} transcripts in {atlas_row['strongest_condition']}."
    if status == "contradicted":
        return f"Comparable driver claim; Marson on-target perturbation moves only {atlas_row['strongest_n_total_de_genes']} transcripts at strongest effect."
    return "The gene lacks comparable on-target Marson coverage."


def build_defended_leaderboard(limit: int = 100) -> dict[str, Any]:
    prereg = _load_json(PREREG_JSON)
    atlas = _load_json(ATLAS_JSON) if ATLAS_JSON.exists() else build_genome_wide_atlas()
    cross_sources = _load_json(CROSS_VALIDATION_SOURCES)
    disease = _load_json(DISEASE_OVERLAY)
    disease_by_gene = {row["gene"]: row for row in disease.get("rows", [])}
    screen_rows = cross_sources.get("screen_rows", {})
    string_network = cross_sources.get("string_network", {})
    dice_expression = cross_sources.get("dice_expression", {})
    _log("phase3 start defended leaderboard")

    candidates = [
        row for row in atlas["rows"]
        if row["typed_status"] == "evidence_attached"
        and not row["standard_t_cell_annotation"]
        and int(row["collectri_target_count"]) == 0
    ]
    decisions = []
    for row in sorted(candidates, key=lambda item: (-(item["strongest_n_total_de_genes"] or 0), item["gene"]))[:limit]:
        gene = row["gene"]
        orthogonal = _orthogonal_dataset_count(row, screen_rows, string_network, dice_expression, disease_by_gene)
        kills = _kill_decisions(row, screen_rows.get(gene), string_network.get(gene), disease_by_gene.get(gene))
        survived = sum(1 for kill in kills if kill["result"] == "survives_current_frozen_evidence")
        failed = [kill for kill in kills if kill["result"] == "fails_pre_registered_kill"]
        open_kills = [kill for kill in kills if kill["result"] == "not_assayed_or_not_cleared"]
        hook = _hook_status(gene, disease_by_gene.get(gene), string_network.get(gene))
        cleared = not failed and not open_kills and orthogonal["covering_dataset_count"] >= 5 and hook["status"] == "evidence_attached"
        decisions.append(
            {
                "gene": gene,
                "typed_status": "evidence_attached",
                "accepted": False,
                "rank_input_strongest_de": row["strongest_n_total_de_genes"],
                "strongest_condition": row["strongest_condition"],
                "rest_de": row["rest_de"],
                "k562_de": row["k562_de"],
                "rpe1_de": row["rpe1_de"],
                "collectri_target_count": row["collectri_target_count"],
                "orthogonal_dataset_count": orthogonal["covering_dataset_count"],
                "orthogonal_datasets": orthogonal["datasets"],
                "real_world_hook": hook,
                "kill_attempts": kills,
                "kill_summary": {
                    "survived": survived,
                    "failed": len(failed),
                    "not_assayed_or_not_cleared": len(open_kills),
                },
                "leaderboard_status": "clears_pre_registered_compute_bar" if cleared else "not_cleared_pre_registered_compute_bar",
                "falsifiable_experiment": _falsifiable_experiment(gene, row),
            }
        )
    decisions.sort(
        key=lambda item: (
            item["leaderboard_status"] != "clears_pre_registered_compute_bar",
            -item["orthogonal_dataset_count"],
            -item["kill_summary"]["survived"],
            -(item["rank_input_strongest_de"] or 0),
            item["gene"],
        )
    )
    for idx, row in enumerate(decisions, start=1):
        row["rank"] = idx
    counts = Counter(row["leaderboard_status"] for row in decisions)
    packet = {
        "phase": "overnight_phase_3_defended_novel_regulator_leaderboard",
        "pre_registration_id": prereg["pre_registration_id"],
        "frontier_root": prereg["frontier_root"],
        "accepted": False,
        "next": "human_signature_required",
        "trust_boundary": "proposal_only",
        "honest_ceiling": HONEST_CEILING,
        "candidate_count_scored": len(decisions),
        "cleared_compute_bar_count": counts.get("clears_pre_registered_compute_bar", 0),
        "not_cleared_count": counts.get("not_cleared_pre_registered_compute_bar", 0),
        "leaderboard": decisions,
        "reproduce_command": "./prospect overnight-compute --phase leaderboard",
    }
    packet["leaderboard_id"] = _hash_obj("overnight_leaderboard", packet)
    LEADERBOARD_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    with LEADERBOARD_CSV.open("w", newline="") as fh:
        fields = ["rank", "gene", "leaderboard_status", "orthogonal_dataset_count", "rank_input_strongest_de", "strongest_condition", "rest_de", "k562_de", "rpe1_de"]
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in decisions:
            writer.writerow({field: row.get(field) for field in fields})
    _log(f"phase3 complete candidates={len(decisions)} cleared={counts.get('clears_pre_registered_compute_bar', 0)} not_cleared={counts.get('not_cleared_pre_registered_compute_bar', 0)}")
    return packet


def _orthogonal_dataset_count(
    row: dict[str, Any],
    screen_rows: dict[str, Any],
    string_network: dict[str, Any],
    dice_expression: dict[str, Any],
    disease_by_gene: dict[str, Any],
) -> dict[str, Any]:
    gene = row["gene"]
    datasets = []
    if row["k562_de"] is not None:
        datasets.append({"name": "Replogle K562", "status": "covered"})
    if row["rpe1_de"] is not None:
        datasets.append({"name": "Replogle RPE1", "status": "covered"})
    if gene in screen_rows:
        screens = screen_rows[gene]
        if any(key.startswith("shifrut") for key in screens):
            datasets.append({"name": "Shifrut 2018 ORCS", "status": "covered"})
        if "schmidt_2022_2427" in screens:
            datasets.append({"name": "Schmidt 2022 ORCS", "status": "orthogonal_phenotype"})
    if gene in string_network:
        datasets.append({"name": "STRING", "status": "covered"})
    if gene in dice_expression:
        datasets.append({"name": "DICE", "status": "covered"})
    if gene in disease_by_gene:
        datasets.append({"name": "Open Targets", "status": "covered"})
    return {"covering_dataset_count": len(datasets), "datasets": datasets}


def _kill_decisions(
    row: dict[str, Any],
    screens: dict[str, Any] | None,
    string_row: dict[str, Any] | None,
    disease_row: dict[str, Any] | None,
) -> list[dict[str, str]]:
    technical = "survives_current_frozen_evidence"
    technical_basis = "on-target Marson perturbation is present at the strongest condition"
    if row["strongest_offtarget_flag"]:
        technical = "fails_pre_registered_kill"
        technical_basis = "strongest Marson row carries an off-target warning"
    artifact = "survives_current_frozen_evidence"
    artifact_basis = f"Rest DE {row['rest_de']}; K562 DE {row['k562_de']}; RPE1 {row['rpe1_de']}"
    if row["rest_de"] > 350 or (row["k562_de"] is not None and row["k562_de"] > K562_SPECIFICITY_WARNING_DE) or (row["rpe1_de"] is not None and row["rpe1_de"] > K562_SPECIFICITY_WARNING_DE):
        artifact = "fails_pre_registered_kill"
    batch = "not_assayed_or_not_cleared"
    batch_basis = "no frozen primary T-cell comparator covers this gene"
    if screens:
        shifrut_hits = [
            key for key, value in screens.items()
            if key.startswith("shifrut") and value.get("hit_status") == "hit"
        ]
        shifrut_non_hits = [
            key for key, value in screens.items()
            if key.startswith("shifrut") and value.get("hit_status") == "non_hit"
        ]
        if shifrut_hits:
            batch = "survives_current_frozen_evidence"
            batch_basis = "supporting Shifrut ORCS hit: " + ", ".join(shifrut_hits)
        elif shifrut_non_hits:
            batch = "fails_pre_registered_kill"
            batch_basis = "covered Shifrut ORCS non-hit: " + ", ".join(shifrut_non_hits)
    reverse = "survives_current_frozen_evidence"
    reverse_basis = "the candidate is selected from causal Marson perturbation, not expression alone"
    alternative = "survives_current_frozen_evidence" if string_row and string_row.get("top_partners") else "not_assayed_or_not_cleared"
    alternative_basis = "STRING partners attached" if alternative == "survives_current_frozen_evidence" else "no frozen STRING mechanism attached"
    if disease_row and disease_row.get("overlay_class") == "no_immune_or_hematologic_context" and alternative == "not_assayed_or_not_cleared":
        alternative_basis = "no STRING mechanism and no selected immune disease context"
    return [
        {"kill_id": "technical_confound", "result": technical, "basis": technical_basis},
        {"kill_id": "essentiality_or_proliferation_artifact", "result": artifact, "basis": artifact_basis},
        {"kill_id": "batch_or_donor_effect", "result": batch, "basis": batch_basis},
        {"kill_id": "reverse_causality_or_passenger_marker", "result": reverse, "basis": reverse_basis},
        {"kill_id": "better_alternative_mechanism", "result": alternative, "basis": alternative_basis},
    ]


def _hook_status(gene: str, disease_row: dict[str, Any] | None, string_row: dict[str, Any] | None) -> dict[str, str]:
    if disease_row and disease_row.get("overlay_class") != "no_immune_or_hematologic_context":
        return {"status": "evidence_attached", "basis": disease_row.get("overlay_class", "")}
    if gene == "PGGT1B":
        return {"status": "evidence_attached", "basis": "existing frozen PGGT1B ChEMBL geranylgeranyl-transferase context"}
    if string_row and string_row.get("top_partners"):
        return {"status": "evidence_attached", "basis": "protein-network mechanism hook"}
    return {"status": "not_assayed_or_not_cleared", "basis": "no frozen disease, druggability, or named-correction hook attached"}


def _falsifiable_experiment(gene: str, row: dict[str, Any]) -> str:
    condition = row["strongest_condition"] or "stimulated"
    return (
        f"CRISPRi knockdown of {gene} in primary human CD4+ T cells at {condition} with at least two guides, "
        "non-targeting and activation-pathway controls, activation-marker flow and RNA readout; refuted if "
        "on-target knockdown does not shift the registered activation program or only shifts a broad viability signature."
    )


def write_report() -> dict[str, Any]:
    atlas = _load_json(ATLAS_JSON)
    literature = _load_json(LITERATURE_AUDIT_JSON)
    leaderboard = _load_json(LEADERBOARD_JSON)
    counts = literature["typed_status_counts"]
    cleared = leaderboard["cleared_compute_bar_count"]
    top = leaderboard["leaderboard"][0] if leaderboard["leaderboard"] else None
    report = {
        "phase": "overnight_compute_report",
        "accepted": False,
        "next": "human_signature_required",
        "honest_ceiling": HONEST_CEILING,
        "atlas_gene_count": atlas["gene_count"],
        "literature_claim_count": literature["claim_count"],
        "literature_contradicted_count": counts.get("contradicted", 0),
        "leaderboard_cleared_count": cleared,
        "top_leaderboard_gene": top["gene"] if top else None,
    }
    lines = [
        "# Overnight compute report",
        "",
        "All outputs are proposal-only and accepted=false. No model is in the trust path. A human key accepts no state in this run.",
        "",
        f"Ceiling: {HONEST_CEILING}",
        "",
        "## Three Numbers",
        "",
        f"- Genome-wide atlas genes typed: {atlas['gene_count']}",
        f"- Literature claims contradicted: {counts.get('contradicted', 0)} of {literature['claim_count']}",
        f"- Defended leaderboard entries clearing the compute bar: {cleared} of {leaderboard['candidate_count_scored']}",
        "",
        "## Phase 1",
        "",
        f"`{atlas['atlas_id']}` scored {atlas['gene_count']} genes. Counts: {atlas['typed_status_counts']}.",
        "",
        "## Phase 2",
        "",
        f"`{literature['audit_id']}` mined {literature['document_count']} Europe PMC records into {literature['claim_count']} typed claims. Counts: {literature['typed_status_counts']}.",
        "",
        "## Phase 3",
        "",
        f"`{leaderboard['leaderboard_id']}` scored {leaderboard['candidate_count_scored']} candidate drivers absent from CollecTRI and standard annotations. Cleared compute bar: {cleared}.",
        "",
        "## Public Artifacts",
        "",
        "- `/data/overnight_preregistration.json`",
        "- `/data/overnight_genome_wide_atlas.json`",
        "- `/data/overnight_literature_claims.json`",
        "- `/data/overnight_literature_audit.json`",
        "- `/data/overnight_defended_leaderboard.json`",
        "",
        "## Reproduce",
        "",
        "```bash",
        "./prospect overnight-compute",
        "```",
    ]
    REPORT_DOC.write_text("\n".join(lines) + "\n")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prospect overnight-compute")
    parser.add_argument("--phase", choices=["all", "atlas", "literature", "leaderboard", "report"], default="all")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.phase in {"all", "atlas"}:
        result = build_genome_wide_atlas()
    if args.phase in {"all", "literature"}:
        result = build_literature_audit()
    if args.phase in {"all", "leaderboard"}:
        result = build_defended_leaderboard()
    if args.phase in {"all", "report"}:
        result = write_report()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
