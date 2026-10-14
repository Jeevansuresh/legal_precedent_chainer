from __future__ import annotations

from collections import defaultdict
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from legal_precedent_chainer.config import PROCESSED_DATA_PATH
from legal_precedent_chainer.data_loader import load_cases
from legal_precedent_chainer.embeddings import EmbeddingProvider
from legal_precedent_chainer.graph_index import build_graph
from legal_precedent_chainer.models import (
    ArgumentExportRequest,
    ArgumentExportResponse,
    CaseResponse,
    PathFindRequest,
    PathFindResponse,
    QuerySuggestionRequest,
    QuerySuggestionResponse,
)
from legal_precedent_chainer.service import PathService
from legal_precedent_chainer.ui import render_home_page

app = FastAPI(title="Legal Precedent Chainer", version="0.3.0")


class AppState:
    service: PathService
    cited_by_count: Dict[str, int]


state = AppState()


def ensure_initialized() -> None:
    if not hasattr(state, "service"):
        on_startup()


@app.on_event("startup")
def on_startup() -> None:
    cases = load_cases(PROCESSED_DATA_PATH)
    provider = EmbeddingProvider()

    case_ids = list(cases.keys())
    summaries = [cases[case_id].summary for case_id in case_ids]
    vectors = provider.embed_many(summaries)
    embedding_map = {case_id: vector for case_id, vector in zip(case_ids, vectors)}

    built = build_graph(cases=cases, embeddings=embedding_map)
    state.service = PathService(built)

    cited_by = defaultdict(int)
    for case in cases.values():
        for cited in case.citations:
            if cited in cases:
                cited_by[cited] += 1

    state.cited_by_count = dict(cited_by)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return render_home_page()


@app.get("/api/cases")
def list_cases() -> list[dict[str, object]]:
    ensure_initialized()
    records = [
        {
            "id": case.id,
            "title": case.title,
            "court": case.court,
            "year": case.year,
            "citation_count": len(case.citations),
            "cited_by_count": state.cited_by_count.get(case.id, 0),
        }
        for case in state.service.built_graph.cases.values()
    ]
    records.sort(key=lambda item: (int(item["year"]), str(item["id"])))
    return records


@app.get("/api/stats")
def dataset_stats() -> dict[str, int | str]:
    ensure_initialized()
    cases = state.service.built_graph.cases
    graph = state.service.built_graph.graph
    courts = {case.court for case in cases.values()}
    years = [case.year for case in cases.values()]
    return {
        "case_count": len(cases),
        "citation_edge_count": graph.number_of_edges(),
        "court_count": len(courts),
        "year_min": min(years) if years else 0,
        "year_max": max(years) if years else 0,
        "mode": "graph+embedding-fusion",
    }


@app.post("/api/query/suggest", response_model=QuerySuggestionResponse)
def suggest_query(request: QuerySuggestionRequest) -> QuerySuggestionResponse:
    ensure_initialized()
    return state.service.suggest_from_question(
        question=request.question,
        practice_context=request.practice_context,
        jurisdiction=request.jurisdiction,
    )


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/case/{case_id}", response_model=CaseResponse)
def get_case(case_id: str) -> CaseResponse:
    ensure_initialized()
    if case_id not in state.service.built_graph.cases:
        raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

    case = state.service.built_graph.cases[case_id]
    return CaseResponse(
        id=case.id,
        title=case.title,
        court=case.court,
        year=case.year,
        summary=case.summary,
        citations=case.citations,
        cited_by_count=state.cited_by_count.get(case.id, 0),
    )


def _resolve_request_cases(request: PathFindRequest) -> tuple[str, str]:
    source = request.source_case_id or request.source_case
    target = request.target_case_id or request.target_case

    if (not source or not target) and request.user_question:
        suggestion = state.service.suggest_from_question(
            question=request.user_question,
            practice_context=request.practice_context,
            jurisdiction=request.jurisdiction,
        )
        source = source or suggestion.inferred_source_case
        target = target or suggestion.inferred_target_case

    if not source or not target:
        raise HTTPException(
            status_code=400,
            detail="Provide source/target cases, or provide user_question for auto-suggestion.",
        )

    return source, target


def _execute_path_request(request: PathFindRequest) -> PathFindResponse:
    source, target = _resolve_request_cases(request)

    try:
        return state.service.find_path(
            source_value=source,
            target_value=target,
            algorithm=request.algorithm,
            alpha=request.alpha,
            beta=request.beta,
            max_depth=request.max_depth,
            practice_context=request.practice_context,
            draft_length=request.draft_length,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/path/find", response_model=PathFindResponse)
def find_path(request: PathFindRequest) -> PathFindResponse:
    ensure_initialized()
    return _execute_path_request(request)


def _build_memo_markdown(response: PathFindResponse) -> str:
    lines = [
        "# Argument Memo",
        "",
        "## Recommended Argument Chain",
        f"- Source: {response.recommended_chain.source_case}",
        f"- Target: {response.recommended_chain.target_case}",
        f"- Path: {' -> '.join(response.recommended_chain.path) if response.recommended_chain.path else 'None'}",
        f"- Persuasive reason: {response.recommended_chain.persuasive_reason}",
        "",
        "## Chain Quality Scorecard",
        f"- Authority strength: {response.chain_scorecard.authority_strength}",
        f"- Coherence score: {response.chain_scorecard.coherence_score}",
        f"- Risk score: {response.chain_scorecard.risk_score}",
        f"- Draft readiness: {response.chain_scorecard.draft_readiness}",
        f"- Notes: {response.chain_scorecard.notes}",
        "",
        "## Lawyer Brief",
        f"**Issue:** {response.lawyer_brief.issue}",
        "",
        f"**Rule:** {response.lawyer_brief.rule}",
        "",
        f"**Application:** {response.lawyer_brief.application}",
        "",
        f"**Conclusion:** {response.lawyer_brief.conclusion}",
        "",
        "## Draft Blocks",
        f"**Neutral paragraph:** {response.lawyer_brief.suggested_paragraph}",
        "",
        f"**Petitioner/Appellant:** {response.lawyer_brief.petitioner_paragraph}",
        "",
        f"**Respondent:** {response.lawyer_brief.respondent_paragraph}",
        "",
        "## Authorities to Read First",
    ]

    for authority in response.lawyer_brief.authorities_to_read_first:
        lines.append(f"- {authority}")

    lines.extend(["", "## Verification Checklist"])
    for item in response.verification_checklist:
        lines.append(f"- {item}")

    lines.extend(["", "## Risk Flags"])
    for risk in response.risk_flags:
        lines.append(f"- [{risk.severity.upper()}] {risk.title}: {risk.reason} | Check: {risk.recommended_check}")

    lines.extend(["", "## Counter-Argument Strategy"])
    lines.append(f"- Likely opposing chain: {' -> '.join(response.counter_argument_pack.likely_opposing_chain)}")
    lines.append(f"- Opposing argument: {response.counter_argument_pack.opposing_argument}")
    lines.append(f"- Rebuttal strategy: {response.counter_argument_pack.rebuttal_strategy}")

    lines.extend(["", "## Disclaimer", response.lawyer_brief.disclaimer])
    return "\n".join(lines)


@app.post("/argument/export", response_model=ArgumentExportResponse)
def export_argument(request: ArgumentExportRequest) -> ArgumentExportResponse:
    ensure_initialized()
    path_request = PathFindRequest(
        source_case_id=request.source_case_id,
        source_case=request.source_case,
        target_case_id=request.target_case_id,
        target_case=request.target_case,
        user_question=request.user_question,
        practice_context=request.practice_context,
        jurisdiction=request.jurisdiction,
        include_off_jurisdiction=request.include_off_jurisdiction,
        algorithm=request.algorithm,
        alpha=request.alpha,
        beta=request.beta,
        max_depth=request.max_depth,
        draft_length=request.draft_length,
    )

    payload = _execute_path_request(path_request)
    memo_markdown = _build_memo_markdown(payload)

    return ArgumentExportResponse(
        format=request.format,
        memo_markdown=memo_markdown,
        payload=payload,
    )
