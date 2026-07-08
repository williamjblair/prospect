"""Normalize common AI-biology outputs into Prospect gene rows."""
from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MARSON_FULL = ROOT / "examples" / "data" / "marson_de_full.csv"

GENE_COLUMNS = [
    "gene",
    "genes",
    "symbol",
    "gene_symbol",
    "gene symbol",
    "marker",
    "markers",
    "feature",
    "target",
    "name",
]

ALIASES = {
    "IL-7R": "IL7R",
    "CD127": "IL7R",
    "CD25": "IL2RA",
    "PD-1": "PDCD1",
    "PD1": "PDCD1",
    "CD279": "PDCD1",
    "PD-L1": "CD274",
    "PDL1": "CD274",
    "B7-H1": "CD274",
    "B7H1": "CD274",
    "TIM3": "HAVCR2",
    "TIM-3": "HAVCR2",
    "LAG-3": "LAG3",
    "CTLA-4": "CTLA4",
    "TIGIT": "TIGIT",
}


def _maps() -> tuple[set[str], dict[str, str]]:
    symbols: set[str] = set()
    ensembl: dict[str, str] = {}
    with MARSON_FULL.open(newline="") as f:
        for row in csv.DictReader(f):
            gene = row["target_contrast_gene_name"].upper()
            symbols.add(gene)
            ens = row["target_contrast"].split(".", 1)[0].upper()
            ensembl.setdefault(ens, gene)
    return symbols, ensembl


SYMBOLS, ENSEMBL_TO_SYMBOL = _maps()


def _clean_identifier(value: Any) -> str:
    text = str(value or "").strip().strip('"').strip("'")
    text = re.sub(r"\s+", "", text)
    return text.upper()


def normalize_identifier(value: Any) -> dict[str, str]:
    original = str(value or "").strip()
    token = _clean_identifier(original)
    if not token:
        return {"gene": "", "input": original, "identifier_kind": "empty"}
    alias = ALIASES.get(token)
    if alias:
        return {"gene": alias, "input": original, "identifier_kind": "alias"}
    ens = token.split(".", 1)[0]
    if ens in ENSEMBL_TO_SYMBOL:
        return {"gene": ENSEMBL_TO_SYMBOL[ens], "input": original, "identifier_kind": "ensembl"}
    if token in SYMBOLS:
        return {"gene": token, "input": original, "identifier_kind": "symbol"}
    return {"gene": token, "input": original, "identifier_kind": "unknown"}


def _extract_json_genes(obj: Any, path: str = "") -> list[tuple[str, str]]:
    genes: list[tuple[str, str]] = []
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, str):
                genes.append((item, path or "list"))
            elif isinstance(item, dict):
                for key in GENE_COLUMNS:
                    if key in {k.lower() for k in item}:
                        actual = next(k for k in item if k.lower() == key)
                        genes.append((str(item[actual]), path or actual))
                        break
    elif isinstance(obj, dict):
        for key, value in obj.items():
            key_l = key.lower()
            if key_l in {"auc", "metrics", "metadata"}:
                continue
            if key_l in GENE_COLUMNS and isinstance(value, str):
                genes.append((value, key))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        genes.append((item, key))
                    elif isinstance(item, dict):
                        genes.extend(_extract_json_genes([item], key))
            elif isinstance(value, dict):
                genes.extend(_extract_json_genes(value, key))
    return genes


def _parse_table(text: str) -> tuple[list[tuple[str, str]], str]:
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    fields = reader.fieldnames or []
    lower = {field.lower().strip(): field for field in fields}
    gene_col = next((lower[col] for col in GENE_COLUMNS if col in lower), None)
    if not gene_col:
        raise ValueError("table input needs a gene, symbol, marker, target, feature, or name column")
    genes: list[tuple[str, str]] = []
    for row in reader:
        value = row.get(gene_col, "")
        if value:
            genes.append((value, gene_col))
    return genes, "table"


def _parse_gene_list(text: str) -> list[tuple[str, str]]:
    tokens = [tok for tok in re.split(r"[\s,;]+", text.strip()) if tok]
    return [(tok, "gene_list") for tok in tokens]


def _dedupe(raw: list[tuple[str, str]]) -> tuple[list[dict[str, str]], list[str]]:
    seen: set[str] = set()
    genes: list[dict[str, str]] = []
    warnings: list[str] = []
    submitted = 0
    for value, source in raw:
        submitted += 1
        norm = normalize_identifier(value)
        gene = norm["gene"]
        if not gene:
            continue
        if gene in seen:
            warnings.append(f"duplicate gene ignored: {gene}")
            continue
        seen.add(gene)
        genes.append({**norm, "source_column": source})
    if not genes:
        raise ValueError("no gene identifiers found in submission")
    return genes, warnings


def parse_submission_text(text: str, filename: str = "") -> dict[str, Any]:
    if not text or not text.strip():
        raise ValueError("submission is empty")
    stripped = text.strip()
    raw: list[tuple[str, str]]
    input_kind = "gene_list"
    if stripped[0] in "[{":
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON submission: {exc.msg}") from exc
        raw = _extract_json_genes(obj)
        input_kind = "signature_json"
    elif "\n" in stripped and ("," in stripped.splitlines()[0] or "\t" in stripped.splitlines()[0]):
        raw, input_kind = _parse_table(stripped)
    else:
        raw = _parse_gene_list(stripped)
    genes, warnings = _dedupe(raw)
    return {
        "input_kind": input_kind,
        "filename": filename,
        "submitted_items": len(raw),
        "unique_genes": len(genes),
        "genes": genes,
        "warnings": warnings,
    }
