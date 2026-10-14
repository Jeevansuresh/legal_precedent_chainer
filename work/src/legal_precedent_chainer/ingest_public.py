from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests


COURTLISTENER_SEARCH_URL = "https://www.courtlistener.com/api/rest/v3/search/"
OYEZ_CASES_URL = "https://api.oyez.org/cases"


def _safe_year(value: Optional[str], fallback: int = 1900) -> int:
    if not value:
        return fallback
    match = re.search(r"(19|20)\\d{2}", str(value))
    return int(match.group(0)) if match else fallback


def _clip(text: str, max_len: int = 1200) -> str:
    text = re.sub(r"\\s+", " ", text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def _normalize_case_id_from_href(href: str) -> Optional[str]:
    if not href:
        return None
    match = re.search(r"/cases/(\\d+)/(\\d+)$", href.strip())
    if not match:
        return None
    term, docket = match.groups()
    return f"OYEZ-{term}-{docket}"


def _extract_citation_tokens(text: str) -> List[tuple[str, str]]:
    if not text:
        return []
    pattern = re.compile(r"\\b(\\d{1,4})\\s+U\\.?S\\.?\\s+(\\d{1,4})\\b", re.IGNORECASE)
    return [(m.group(1), m.group(2)) for m in pattern.finditer(text)]


def fetch_courtlistener_cases(
    query: str,
    max_results: int = 100,
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    params = {
        "q": query,
        "type": "o",
        "order_by": "score desc",
        "stat_Precedential": "on",
        "page_size": min(max_results, 100),
    }

    headers: Dict[str, str] = {}
    key = api_key or os.getenv("COURTLISTENER_API_KEY", "")
    if key:
        headers["Authorization"] = f"Token {key}"

    response = requests.get(COURTLISTENER_SEARCH_URL, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    payload = response.json()

    normalized: List[Dict[str, Any]] = []
    for item in payload.get("results", []):
        cluster_id = item.get("cluster_id") or item.get("id")
        if not cluster_id:
            continue

        normalized.append(
            {
                "id": f"CL-{cluster_id}",
                "title": item.get("caseName") or item.get("caseNameFull") or f"CourtListener Case {cluster_id}",
                "court": item.get("court") or "unknown",
                "year": _safe_year(item.get("dateFiled"), fallback=1900),
                "summary": _clip(item.get("snippet") or ""),
                "citations": [],
                "source": "courtlistener",
            }
        )

    return normalized


def fetch_oyez_cases(max_pages: int = 20, page_size_limit: int = 30, sleep_seconds: float = 0.05) -> List[Dict[str, Any]]:
    collected: List[Dict[str, Any]] = []
    by_id: Dict[str, Dict[str, Any]] = {}
    citation_index: Dict[tuple[str, str], str] = {}

    for page in range(1, max_pages + 1):
        response = requests.get(OYEZ_CASES_URL, params={"page": page}, timeout=30)
        response.raise_for_status()
        listing = response.json()
        if not isinstance(listing, list) or not listing:
            break

        listing = listing[:page_size_limit]

        for item in listing:
            href = item.get("href")
            if not href:
                continue

            detail_resp = requests.get(href, timeout=30)
            detail_resp.raise_for_status()
            detail = detail_resp.json()

            case_id = _normalize_case_id_from_href(href) or f"OYEZ-{item.get('ID')}"
            if case_id in by_id:
                continue

            title = detail.get("name") or item.get("name") or case_id
            citation = detail.get("citation") or {}
            citation_token = None
            if citation.get("volume") and citation.get("page"):
                citation_token = (str(citation.get("volume")), str(citation.get("page")))

            year = _safe_year(str(citation.get("year") or detail.get("term") or item.get("term") or ""), fallback=1900)
            summary_parts = [
                detail.get("description") or "",
                detail.get("facts_of_the_case") or "",
                detail.get("question") or "",
                detail.get("conclusion") or "",
            ]
            summary = _clip(" ".join(part for part in summary_parts if part))
            if not summary:
                summary = _clip(f"{title}. Term {detail.get('term') or item.get('term') or 'unknown'}.")

            citations: List[str] = []

            related_cases = detail.get("related_cases")
            if isinstance(related_cases, list):
                for related in related_cases:
                    related_id = _normalize_case_id_from_href((related or {}).get("href", ""))
                    if related_id and related_id != case_id:
                        citations.append(related_id)

            case_record = {
                "id": case_id,
                "title": title,
                "court": "U.S. Supreme Court",
                "year": year,
                "summary": summary,
                "citations": sorted(set(citations)),
                "source": "oyez",
                "citation_volume": str(citation.get("volume") or ""),
                "citation_page": str(citation.get("page") or ""),
            }

            by_id[case_id] = case_record
            if citation_token:
                citation_index[citation_token] = case_id

            time.sleep(sleep_seconds)

    # Secondary pass: infer additional citation edges from textual citation references.
    for case in by_id.values():
        refs = _extract_citation_tokens(case.get("summary", ""))
        for token in refs:
            cited_case_id = citation_index.get(token)
            if cited_case_id and cited_case_id != case["id"]:
                case["citations"].append(cited_case_id)
        case["citations"] = sorted(set(case["citations"]))

    collected.extend(by_id.values())
    return sorted(collected, key=lambda row: (int(row.get("year", 1900)), row.get("id", "")))


def _merge_cases(primary: Iterable[Dict[str, Any]], secondary: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}

    for entry in list(primary) + list(secondary):
        case_id = entry["id"]
        if case_id not in merged:
            merged[case_id] = {
                "id": case_id,
                "title": entry.get("title", ""),
                "court": entry.get("court", "unknown"),
                "year": int(entry.get("year", 1900)),
                "summary": entry.get("summary", ""),
                "citations": list(entry.get("citations", [])),
            }
            continue

        current = merged[case_id]
        if len(entry.get("summary", "")) > len(current.get("summary", "")):
            current["summary"] = entry.get("summary", current.get("summary", ""))
        if entry.get("title") and not current.get("title"):
            current["title"] = entry["title"]
        if entry.get("court") and current.get("court") in {"", "unknown"}:
            current["court"] = entry["court"]
        if int(entry.get("year", 1900)) != 1900 and int(current.get("year", 1900)) == 1900:
            current["year"] = int(entry["year"])

        current["citations"] = sorted(set(current.get("citations", []) + list(entry.get("citations", []))))

    return sorted(merged.values(), key=lambda row: (int(row.get("year", 1900)), row.get("id", "")))


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch public case data for Legal Precedent Chainer.")
    parser.add_argument("--source", choices=["oyez", "courtlistener", "hybrid"], default="oyez")
    parser.add_argument("--query", default="India Supreme Court precedent")
    parser.add_argument("--max-results", type=int, default=100)
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--raw-output", default="data/raw/public_cases_sample.json")
    parser.add_argument("--processed-output", default="data/processed/cases_seed.json")
    parser.add_argument("--base-processed", default="data/processed/cases_seed.json")
    parser.add_argument("--merge-base", action="store_true", default=True)
    parser.add_argument("--replace", action="store_true", help="Do not merge with base processed file.")
    args = parser.parse_args()

    fetched: List[Dict[str, Any]] = []

    if args.source in {"oyez", "hybrid"}:
        fetched.extend(fetch_oyez_cases(max_pages=args.max_pages))

    if args.source in {"courtlistener", "hybrid"}:
        try:
            fetched.extend(fetch_courtlistener_cases(query=args.query, max_results=args.max_results))
        except requests.HTTPError as exc:
            print(f"CourtListener fetch failed: {exc}. Continuing with available sources.")

    if not fetched:
        raise RuntimeError("No records fetched from public sources.")

    base_data: List[Dict[str, Any]] = []
    use_merge = args.merge_base and not args.replace
    if use_merge:
        base_path = Path(args.base_processed)
        if base_path.exists():
            payload = json.loads(base_path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                base_data = payload

    merged = _merge_cases(base_data, fetched) if use_merge else _merge_cases([], fetched)

    raw_output_path = Path(args.raw_output)
    raw_output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_output_path.write_text(json.dumps(fetched, indent=2), encoding="utf-8")

    processed_output_path = Path(args.processed_output)
    processed_output_path.parent.mkdir(parents=True, exist_ok=True)
    processed_output_path.write_text(json.dumps(merged, indent=2), encoding="utf-8")

    total_edges = sum(len(row.get("citations", [])) for row in merged)
    years = [int(row.get("year", 1900)) for row in merged if int(row.get("year", 1900)) > 0]
    print(f"Fetched {len(fetched)} public records.")
    print(f"Processed dataset now has {len(merged)} cases and {total_edges} citation edges.")
    if years:
        print(f"Coverage years: {min(years)}-{max(years)}")
    print(f"Raw saved to: {raw_output_path}")
    print(f"Processed saved to: {processed_output_path}")


if __name__ == "__main__":
    main()
