#!/usr/bin/env python3
"""
Import full term datasets from ../Resources into data/*.json for glossary generation.

This script converts the app resource schema (words + metadata) into the web glossary
schema used by scripts/generate-glossary.py.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


CATEGORY_CONFIG: Dict[str, Dict[str, object]] = {
    "Aviations": {
        "slug": "aviation",
        "name": "Aviation English",
        "description": "Aviation English terminology sourced from ICAO Doc 9432 and FAA Pilot/Controller Glossary for pilots, ATCs and aviation professionals.",
        "source": "ICAO Doc 9432, FAA PCG",
        "targetAudience": ["Pilots", "Air Traffic Controllers", "Cabin Crew"],
        "examRelevance": ["ICAO Level 4", "ICAO Level 5", "ICAO Level 6", "EASA FCL.055"],
    },
    "Maritime": {
        "slug": "maritime",
        "name": "Maritime English",
        "description": "Maritime English terminology based on IMO SMCP, STCW and SOLAS standards for deck, bridge and engine operations.",
        "source": "IMO SMCP, STCW Convention, SOLAS, COLREG",
        "targetAudience": ["Deck Officers", "Engine Officers", "Masters"],
        "examRelevance": ["STCW", "Marlins Test", "ISF Watchkeeper", "GMDSS"],
    },
    "Logistics": {
        "slug": "logistics",
        "name": "Logistics English",
        "description": "Logistics and supply chain terminology covering Incoterms 2020, freight forwarding, customs documentation and supply chain KPIs for international trade professionals.",
        "source": "Incoterms 2020 (ICC), FIATA, IATA DGR, WCO",
        "targetAudience": ["Freight Forwarders", "Supply Chain Managers", "Customs Brokers"],
        "examRelevance": ["FIATA Diploma", "CILT Certification", "IATA DGR"],
    },
    "Finance": {
        "slug": "finance",
        "name": "Finance English",
        "description": "Finance and banking terminology for capital markets, corporate finance, accounting standards and fintech operations.",
        "source": "CFA Institute, IFRS Foundation, FASB (GAAP), Basel III Framework",
        "targetAudience": ["Financial Analysts", "Bankers", "Traders"],
        "examRelevance": ["CFA", "ACCA", "FRM"],
    },
    "Cybersecurity": {
        "slug": "cybersecurity",
        "name": "Cybersecurity English",
        "description": "Cybersecurity and information security terminology aligned with ISO 27001, NIST and MITRE ATT&CK frameworks.",
        "source": "ISO 27001, NIST Cybersecurity Framework, MITRE ATT&CK",
        "targetAudience": ["SOC Analysts", "Security Engineers", "Incident Responders"],
        "examRelevance": ["CISSP", "CompTIA Security+", "CEH"],
    },
    "ItDevs": {
        "slug": "it-devops",
        "name": "IT/DevOps English",
        "description": "Cloud, DevOps and IT service management terminology covering CI/CD, observability, IaC and ITIL practices.",
        "source": "ITIL v4, AWS Well-Architected Framework, Kubernetes Documentation, CNCF",
        "targetAudience": ["DevOps Engineers", "SREs", "Platform Engineers"],
        "examRelevance": ["AWS Certification", "Azure Certification", "ITIL v4", "CKA/CKAD"],
    },
}

FILE_TOKEN_MAP = {
    "atc": "ATC",
    "cicd": "CI/CD",
    "k8s": "Kubernetes",
    "iac": "Infrastructure as Code",
    "cfg": "Configuration",
    "obs": "Observability",
    "vcs": "Version Control",
    "sre": "Site Reliability Engineering",
    "grc": "Governance Risk Compliance",
    "soc": "SOC",
    "app": "Application Security",
    "net": "Network Security",
    "vuln": "Vulnerability Management",
    "crypto": "Cryptography",
    "cloudops": "Cloud Operations",
    "customs": "Customs",
    "docs": "Transport Documents",
    "incoterms": "Incoterms 2020",
    "mode": "Transport Modes",
    "vis": "Visibility and Tracking",
    "whse": "Warehousing",
    "dg": "Dangerous Goods",
    "mnv": "Maneuvering",
    "met": "Meteorology",
    "engr": "Engineering",
    "emg": "Emergency Communication",
    "ext": "External Communication",
    "mel": "MEL and CDL",
    "cdl": "MEL and CDL",
}

DIR_PREFIXES = {
    "Aviations": "aviation_",
    "Maritime": "maritime_",
    "Logistics": "logistics_",
    "Finance": "finance_",
    "Cybersecurity": "cyber_",
    "ItDevs": "it_",
}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def clean_json_text(raw: str) -> str:
    # Handles resource files that accidentally include trailing commas before ] or }.
    return re.sub(r",\s*([}\]])", r"\1", raw)


def load_json_lenient(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return json.loads(clean_json_text(raw))


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_translation_map(raw_map: object) -> dict:
    if not isinstance(raw_map, dict):
        return {}
    cleaned = {}
    for lang, value in raw_map.items():
        lang_key = normalize_whitespace(str(lang)).lower()
        text = normalize_whitespace(str(value))
        if lang_key and text:
            cleaned[lang_key] = text
    return cleaned


def subcategory_from_filename(resource_dir: str, filename: str) -> str:
    stem = filename.replace("_words.json", "")
    prefix = DIR_PREFIXES.get(resource_dir, "")
    if prefix and stem.startswith(prefix):
        stem = stem[len(prefix) :]
    tokens = [token for token in stem.split("_") if token]
    mapped_tokens = [FILE_TOKEN_MAP.get(token, token.capitalize()) for token in tokens]
    subcategory = " ".join(mapped_tokens).strip()
    return subcategory or "Core Terms"


def first_example_sentence(word_obj: dict) -> str:
    examples = word_obj.get("examples", [])
    if isinstance(examples, list):
        for item in examples:
            if isinstance(item, dict):
                sentence = normalize_whitespace(item.get("sentence", ""))
                if sentence:
                    return sentence
    contextual = normalize_whitespace(word_obj.get("contextualUsage", ""))
    if contextual:
        return contextual
    return ""


def first_example_translations(word_obj: dict) -> dict:
    examples = word_obj.get("examples", [])
    if not isinstance(examples, list):
        return {}

    for item in examples:
        if not isinstance(item, dict):
            continue
        cleaned = normalize_translation_map(item.get("translation", {}))
        if cleaned:
            return cleaned
    return {}


def unique_slug(base: str, fallback_id: str, used_slugs: set) -> str:
    base_slug = slugify(base) or "term"
    if base_slug not in used_slugs:
        used_slugs.add(base_slug)
        return base_slug

    id_slug = slugify(fallback_id or "")
    if id_slug:
        candidate = f"{base_slug}-{id_slug}"
        if candidate not in used_slugs:
            used_slugs.add(candidate)
            return candidate

    i = 2
    while f"{base_slug}-{i}" in used_slugs:
        i += 1
    candidate = f"{base_slug}-{i}"
    used_slugs.add(candidate)
    return candidate


def build_related_terms(terms: List[dict], max_related: int = 4) -> None:
    tag_index: Dict[str, set] = defaultdict(set)
    subcategory_index: Dict[str, set] = defaultdict(set)
    slug_lookup: Dict[str, set] = defaultdict(set)

    for idx, term in enumerate(terms):
        for tag in term["_tags"]:
            tag_index[tag].add(idx)
        subcategory_index[term["subcategory"]].add(idx)
        slug_lookup[slugify(term["term"])].add(idx)

    for idx, term in enumerate(terms):
        scores: Dict[int, float] = defaultdict(float)

        for tag in term["_tags"]:
            for candidate_idx in tag_index[tag]:
                if candidate_idx != idx:
                    scores[candidate_idx] += 3.0

        for candidate_idx in subcategory_index[term["subcategory"]]:
            if candidate_idx != idx:
                scores[candidate_idx] += 1.25

        for synonym in term["_synonyms"]:
            s_slug = slugify(synonym)
            for candidate_idx in slug_lookup.get(s_slug, set()):
                if candidate_idx != idx:
                    scores[candidate_idx] += 5.0

        ranked_candidates = sorted(
            scores.items(),
            key=lambda item: (
                -item[1],
                -terms[item[0]]["_usage_frequency"],
                terms[item[0]]["term"].lower(),
            ),
        )
        term["relatedTerms"] = [
            terms[candidate_idx]["slug"] for candidate_idx, _ in ranked_candidates[:max_related]
        ]


def convert_category(resource_dir: Path, config: Dict[str, object]) -> Tuple[dict, int]:
    terms: List[dict] = []
    seen_exact = set()
    used_slugs = set()

    for file_path in sorted(resource_dir.glob("*.json")):
        data = load_json_lenient(file_path)
        words = data.get("words", [])
        if not isinstance(words, list):
            continue

        fallback_subcategory = subcategory_from_filename(resource_dir.name, file_path.name)
        for raw_word in words:
            if not isinstance(raw_word, dict):
                continue

            term_name = normalize_whitespace(raw_word.get("word", ""))
            definition = normalize_whitespace(raw_word.get("definition", ""))
            if not term_name or not definition:
                continue

            dedupe_key = (term_name.lower(), definition.lower())
            if dedupe_key in seen_exact:
                continue
            seen_exact.add(dedupe_key)

            slug = unique_slug(term_name, str(raw_word.get("id", "")), used_slugs)
            usage = first_example_sentence(raw_word)
            usage_translations = first_example_translations(raw_word)
            term_translations = normalize_translation_map(raw_word.get("translation", {}))
            definition_translations = {}
            for field_name in [
                "definitionTranslations",
                "definitionTranslation",
                "definition_translation",
            ]:
                definition_translations = normalize_translation_map(raw_word.get(field_name, {}))
                if definition_translations:
                    break
            tags = [
                normalize_whitespace(tag).lower()
                for tag in (raw_word.get("tags") or [])
                if normalize_whitespace(str(tag))
            ]
            synonyms = [
                normalize_whitespace(item)
                for item in (raw_word.get("synonyms") or [])
                if normalize_whitespace(str(item))
            ]
            subcategory = fallback_subcategory

            terms.append(
                {
                    "term": term_name,
                    "slug": slug,
                    "abbreviation": None,
                    "definition": definition,
                    "definitionTranslations": definition_translations,
                    "subcategory": subcategory,
                    "source": config["source"],
                    "usage": usage,
                    "termTranslations": term_translations,
                    "usageTranslations": usage_translations,
                    "relatedTerms": [],
                    "examRelevance": list(config["examRelevance"]),
                    "targetAudience": list(config["targetAudience"]),
                    "_tags": tags,
                    "_synonyms": synonyms,
                    "_usage_frequency": int(raw_word.get("usageFrequency", 0) or 0),
                }
            )

    build_related_terms(terms, max_related=4)

    for term in terms:
        term.pop("_tags", None)
        term.pop("_synonyms", None)
        term.pop("_usage_frequency", None)

    category_block = {
        "name": config["name"],
        "slug": config["slug"],
        "description": config["description"],
        "source": config["source"],
        "termCount": f"{len(terms):,}+",
    }
    payload = {"category": category_block, "terms": terms}
    return payload, len(terms)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import glossary terms from app Resources.")
    parser.add_argument(
        "--resources-dir",
        default=str(Path(__file__).resolve().parents[2] / "Resources"),
        help="Path to source resources directory (default: ../Resources)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "data"),
        help="Output directory for converted data JSON files (default: data/)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    resources_root = Path(args.resources_dir).resolve()
    output_root = Path(args.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    if not resources_root.exists():
        raise SystemExit(f"Resources directory not found: {resources_root}")

    grand_total = 0
    print(f"Importing resources from: {resources_root}")
    for resource_folder, config in CATEGORY_CONFIG.items():
        src_dir = resources_root / resource_folder
        if not src_dir.exists():
            print(f"Skipping missing category directory: {src_dir}")
            continue

        payload, count = convert_category(src_dir, config)
        out_file = output_root / f"{config['slug']}.json"
        out_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        grand_total += count
        print(f"- {config['slug']}: {count} terms -> {out_file}")

    print(f"Done. Imported {grand_total} total terms.")


if __name__ == "__main__":
    main()
