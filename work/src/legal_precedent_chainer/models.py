from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AlgorithmName(str, Enum):
    bfs = "bfs"
    bellman_ford = "bellman_ford"
    dijkstra = "dijkstra"
    astar = "astar"
    floyd = "floyd"


class DraftLength(str, Enum):
    short = "short"
    standard = "standard"
    long = "long"


class CaseRecord(BaseModel):
    id: str
    title: str
    court: str
    year: int
    summary: str
    citations: List[str] = Field(default_factory=list)


class GraphIndex(BaseModel):
    adjacency: Dict[str, List[str]]
    embeddings: Dict[str, List[float]]
    metadata: Dict[str, CaseRecord]


class QuerySuggestionRequest(BaseModel):
    question: str
    practice_context: Optional[str] = None
    jurisdiction: Optional[str] = None


class QuerySuggestionResponse(BaseModel):
    question: str
    inferred_source_case: str
    inferred_target_case: str
    reasoning: str


class PathFindRequest(BaseModel):
    source_case_id: Optional[str] = None
    source_case: Optional[str] = None
    target_case_id: Optional[str] = None
    target_case: Optional[str] = None
    user_question: Optional[str] = None
    practice_context: Optional[str] = None
    jurisdiction: Optional[str] = None
    include_off_jurisdiction: bool = False
    algorithm: AlgorithmName = AlgorithmName.dijkstra
    alpha: float = Field(default=1.0, ge=0.0, le=10.0)
    beta: float = Field(default=2.0, ge=0.0, le=10.0)
    max_depth: int = Field(default=25, ge=1, le=250)
    draft_length: DraftLength = DraftLength.standard


class HopDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_case: str = Field(alias="from")
    to_case: str = Field(alias="to")
    citation_exists: bool
    similarity: float
    edge_cost: float
    from_summary_snippet: str
    to_summary_snippet: str
    why_hop: str


class PathMetrics(BaseModel):
    total_cost: float
    hop_count: int
    runtime_ms: float
    algorithm: AlgorithmName


class ChainScorecard(BaseModel):
    authority_strength: float
    coherence_score: float
    risk_score: float
    draft_readiness: float
    notes: str


class LawyerBrief(BaseModel):
    issue: str
    rule: str
    application: str
    conclusion: str
    suggested_paragraph: str
    petitioner_paragraph: str
    respondent_paragraph: str
    authorities_to_read_first: List[str]
    disclaimer: str


class SentenceCitation(BaseModel):
    sentence_id: str
    text: str
    supports: List[str]


class RiskFlag(BaseModel):
    severity: str
    title: str
    reason: str
    hop_index: Optional[int] = None
    recommended_check: str


class RecommendedChain(BaseModel):
    source_case: str
    target_case: str
    path: List[str]
    persuasive_reason: str


class AlternativePath(BaseModel):
    strategy_label: str
    when_to_prefer: str
    path: List[str]
    metrics: PathMetrics
    rationale: str


class CounterArgumentPack(BaseModel):
    likely_opposing_chain: List[str]
    opposing_argument: str
    rebuttal_strategy: str


class PathFindResponse(BaseModel):
    path: List[str]
    hops: List[HopDetail]
    metrics: PathMetrics
    explanation: str
    recommended_chain: RecommendedChain
    chain_scorecard: ChainScorecard
    lawyer_brief: LawyerBrief
    verification_checklist: List[str]
    alternatives: List[AlternativePath]
    counter_argument_pack: CounterArgumentPack
    risk_flags: List[RiskFlag]
    sentence_citations: List[SentenceCitation]
    generation_meta: Dict[str, str | float]


class ArgumentExportRequest(BaseModel):
    source_case_id: Optional[str] = None
    source_case: Optional[str] = None
    target_case_id: Optional[str] = None
    target_case: Optional[str] = None
    user_question: Optional[str] = None
    practice_context: Optional[str] = None
    jurisdiction: Optional[str] = None
    include_off_jurisdiction: bool = False
    algorithm: AlgorithmName = AlgorithmName.dijkstra
    alpha: float = Field(default=1.0, ge=0.0, le=10.0)
    beta: float = Field(default=2.0, ge=0.0, le=10.0)
    max_depth: int = Field(default=25, ge=1, le=250)
    draft_length: DraftLength = DraftLength.standard
    format: str = Field(default="json")


class ArgumentExportResponse(BaseModel):
    format: str
    memo_markdown: str
    payload: PathFindResponse


class CaseResponse(BaseModel):
    id: str
    title: str
    court: str
    year: int
    summary: str
    citations: List[str]
    cited_by_count: int
