from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from legal_precedent_chainer import config
from legal_precedent_chainer.algorithms import (
    SearchResult,
    astar_path,
    bellman_ford_path,
    bfs_path,
    dijkstra_path,
    floyd_warshall_path,
)
from legal_precedent_chainer.graph_index import BuiltGraph, cosine_similarity
from legal_precedent_chainer.models import (
    AlgorithmName,
    AlternativePath,
    ChainScorecard,
    CounterArgumentPack,
    DraftLength,
    HopDetail,
    LawyerBrief,
    PathFindResponse,
    PathMetrics,
    QuerySuggestionResponse,
    RecommendedChain,
    RiskFlag,
    SentenceCitation,
)
from legal_precedent_chainer.narration import AzureNarrationClient


@dataclass
class CandidatePath:
    algorithm: AlgorithmName
    path: List[str]
    hops: List[HopDetail]
    metrics: PathMetrics


class PathService:
    def __init__(self, built_graph: BuiltGraph):
        self.built_graph = built_graph
        self.narration_client = AzureNarrationClient()

    @staticmethod
    def _snippet(text: str, max_len: int = 180) -> str:
        compact = " ".join(text.strip().split())
        if len(compact) <= max_len:
            return compact
        return compact[: max_len - 3] + "..."

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return set(re.findall(r"[a-zA-Z]{3,}", text.lower()))

    def suggest_from_question(self, question: str, practice_context: str | None = None, jurisdiction: str | None = None) -> QuerySuggestionResponse:
        query_tokens = self._tokenize(question)
        if not query_tokens:
            fallback_ids = list(self.built_graph.cases.keys())
            return QuerySuggestionResponse(
                question=question,
                inferred_source_case=fallback_ids[0],
                inferred_target_case=fallback_ids[-1],
                reasoning="Question lacked legal keywords; defaulting to first and latest available authorities.",
            )

        scored: List[tuple[float, str]] = []
        for case_id, case in self.built_graph.cases.items():
            case_tokens = self._tokenize(f"{case.title} {case.summary}")
            overlap = len(query_tokens.intersection(case_tokens))
            if overlap == 0:
                continue
            # bias toward doctrinal anchors via indegree and older year for source
            indegree = self.built_graph.graph.in_degree(case_id)
            score = overlap * 5 + indegree * 1.5 + (2100 - case.year) * 0.005
            scored.append((score, case_id))

        if not scored:
            fallback_ids = list(self.built_graph.cases.keys())
            return QuerySuggestionResponse(
                question=question,
                inferred_source_case=fallback_ids[0],
                inferred_target_case=fallback_ids[-1],
                reasoning="No strong keyword match found; using default anchor and target.",
            )

        scored.sort(reverse=True)
        source_case = scored[0][1]

        source_record = self.built_graph.cases[source_case]
        if source_record.citations:
            cited_candidates = [case_id for case_id in source_record.citations if case_id in self.built_graph.cases]
            if cited_candidates:
                cited_candidates.sort(key=lambda cid: self.built_graph.cases[cid].year)
                target_case = cited_candidates[0]
            else:
                target_case = scored[min(1, len(scored) - 1)][1]
        else:
            target_case = scored[min(1, len(scored) - 1)][1]

        reasoning = (
            f"Mapped question keywords to {source_case} as the current-matter target and selected {target_case} "
            f"as supporting authority based on citation links and precedence"
        )
        if practice_context:
            reasoning += f" for {practice_context} context"
        if jurisdiction:
            reasoning += f" within {jurisdiction} focus"

        return QuerySuggestionResponse(
            question=question,
            inferred_source_case=source_case,
            inferred_target_case=target_case,
            reasoning=reasoning + ".",
        )

    def _resolve_case(self, value: str) -> Optional[str]:
        if value in self.built_graph.cases:
            return value

        needle = value.strip().lower()
        for case_id, case in self.built_graph.cases.items():
            if case.title.lower() == needle:
                return case_id
            if needle in case.title.lower():
                return case_id

        return None

    def _edge_cost(self, alpha: float, beta: float):
        def inner(from_case: str, to_case: str) -> float:
            from_vec = self.built_graph.embeddings[from_case]
            to_vec = self.built_graph.embeddings[to_case]
            similarity = max(-1.0, min(1.0, cosine_similarity(from_vec, to_vec)))
            return alpha * 1.0 + beta * (1.0 - similarity)

        return inner

    def _heuristic(self, target: str, alpha: float, beta: float):
        target_vec = self.built_graph.embeddings[target]

        def h(node: str) -> float:
            sim = max(-1.0, min(1.0, cosine_similarity(self.built_graph.embeddings[node], target_vec)))
            return alpha * 0.5 + beta * (1.0 - sim)

        return h

    def _build_hops(self, path: List[str], edge_cost_fn) -> Tuple[List[HopDetail], float]:
        hops: List[HopDetail] = []
        total_cost = 0.0

        for idx in range(len(path) - 1):
            current_case = path[idx]
            next_case = path[idx + 1]
            current_record = self.built_graph.cases[current_case]
            next_record = self.built_graph.cases[next_case]
            sim = cosine_similarity(self.built_graph.embeddings[current_case], self.built_graph.embeddings[next_case])
            edge_cost = edge_cost_fn(current_case, next_case)
            total_cost += edge_cost
            why_hop = (
                f"{current_record.title} cites {next_record.title}; this hop carries the argument from "
                f"{current_record.year} to {next_record.year}."
            )
            hops.append(
                HopDetail(
                    **{
                        "from": current_case,
                        "to": next_case,
                        "citation_exists": self.built_graph.graph.has_edge(current_case, next_case),
                        "similarity": round(float(sim), 4),
                        "edge_cost": round(float(edge_cost), 4),
                        "from_summary_snippet": self._snippet(current_record.summary),
                        "to_summary_snippet": self._snippet(next_record.summary),
                        "why_hop": why_hop,
                    }
                )
            )

        return hops, total_cost

    def _run_algorithm(
        self,
        source: str,
        target: str,
        algorithm: AlgorithmName,
        alpha: float,
        beta: float,
        max_depth: int,
    ) -> Optional[CandidatePath]:
        edge_cost_fn = self._edge_cost(alpha=alpha, beta=beta)

        start_time = time.perf_counter()
        result: Optional[SearchResult]

        if algorithm == AlgorithmName.bfs:
            result = bfs_path(self.built_graph.graph, source, target, max_depth=max_depth)
        elif algorithm == AlgorithmName.bellman_ford:
            result = bellman_ford_path(self.built_graph.graph, source, target, edge_cost=edge_cost_fn)
        elif algorithm == AlgorithmName.dijkstra:
            result = dijkstra_path(self.built_graph.graph, source, target, edge_cost=edge_cost_fn)
        elif algorithm == AlgorithmName.astar:
            result = astar_path(
                self.built_graph.graph,
                source,
                target,
                edge_cost=edge_cost_fn,
                heuristic=self._heuristic(target, alpha=alpha, beta=beta),
            )
        elif algorithm == AlgorithmName.floyd:
            result = floyd_warshall_path(self.built_graph.graph, source, target, edge_cost=edge_cost_fn)
            if result is None:
                result = bellman_ford_path(self.built_graph.graph, source, target, edge_cost=edge_cost_fn)
        else:
            result = None

        runtime_ms = (time.perf_counter() - start_time) * 1000.0

        if result is None:
            return None

        hops, total_cost = self._build_hops(result.path, edge_cost_fn)
        return CandidatePath(
            algorithm=algorithm,
            path=result.path,
            hops=hops,
            metrics=PathMetrics(
                total_cost=round(float(total_cost), 4),
                hop_count=max(0, len(result.path) - 1),
                runtime_ms=round(runtime_ms, 3),
                algorithm=algorithm,
            ),
        )

    def _dedupe_candidates(self, candidates: List[CandidatePath]) -> List[CandidatePath]:
        seen: set[tuple[str, ...]] = set()
        unique: List[CandidatePath] = []
        for candidate in candidates:
            key = tuple(candidate.path)
            if key in seen:
                continue
            seen.add(key)
            unique.append(candidate)
        return unique

    def _build_alternatives(self, candidates: List[CandidatePath]) -> List[AlternativePath]:
        if not candidates:
            return []

        most_direct = min(candidates, key=lambda item: (item.metrics.hop_count, item.metrics.total_cost))
        most_coherent = min(candidates, key=lambda item: item.metrics.total_cost)
        conservative = min(
            candidates,
            key=lambda item: max((hop.edge_cost for hop in item.hops), default=float("inf")),
        )

        labeled = [
            (
                "Most direct",
                most_direct,
                "Use when the judge expects a short authority bridge.",
                "Shortest citation-hops path.",
            ),
            (
                "Most doctrinally coherent",
                most_coherent,
                "Use when issue-continuity is more persuasive than brevity.",
                "Best semantic continuity under weighted scoring.",
            ),
            (
                "Most conservative",
                conservative,
                "Use when you want to minimize weak single-hop links.",
                "Lowest worst-hop risk across candidate methods.",
            ),
        ]

        used: set[tuple[str, ...]] = set()
        alternatives: List[AlternativePath] = []
        for label, candidate, when_to_prefer, rationale in labeled:
            key = tuple(candidate.path)
            if key in used:
                continue
            used.add(key)
            alternatives.append(
                AlternativePath(
                    strategy_label=label,
                    when_to_prefer=when_to_prefer,
                    path=candidate.path,
                    metrics=candidate.metrics,
                    rationale=rationale,
                )
            )
            if len(alternatives) >= max(1, config.MAX_ALTERNATIVES):
                break

        return alternatives

    def _counter_argument_pack(self, alternatives: List[AlternativePath], primary_path: List[str]) -> CounterArgumentPack:
        fallback_path = alternatives[-1].path if alternatives else primary_path
        opposing_argument = (
            "Opposing counsel may prefer the shortest or older-authority chain to argue your selected path is overfitted "
            "to semantic similarity rather than strict doctrinal necessity."
        )
        rebuttal_strategy = (
            "Respond by emphasizing that each selected hop is citation-valid and contextually aligned with the present issue, "
            "then distinguish opposing hops that are procedurally related but doctrinally weak."
        )
        return CounterArgumentPack(
            likely_opposing_chain=fallback_path,
            opposing_argument=opposing_argument,
            rebuttal_strategy=rebuttal_strategy,
        )

    def _chain_scorecard(self, path: List[str], hops: List[HopDetail], risk_flags: List[RiskFlag]) -> ChainScorecard:
        def clamp_0_100(value: float) -> float:
            return round(max(0.0, min(100.0, value)), 2)

        if not path:
            return ChainScorecard(
                authority_strength=0.0,
                coherence_score=0.0,
                risk_score=100.0,
                draft_readiness=0.0,
                notes="No valid chain available.",
            )

        indegree_values = [self.built_graph.graph.in_degree(case_id) for case_id in path]
        avg_indegree = (sum(indegree_values) / len(indegree_values)) if indegree_values else 0.0
        authority_strength = clamp_0_100(35.0 + avg_indegree * 6.5)

        similarities = [hop.similarity for hop in hops] or [0.0]
        avg_similarity = sum(similarities) / len(similarities)
        coherence_score = clamp_0_100((avg_similarity + 1.0) * 50.0)

        high_count = sum(1 for risk in risk_flags if risk.severity == "high")
        medium_count = sum(1 for risk in risk_flags if risk.severity == "medium")
        low_count = sum(1 for risk in risk_flags if risk.severity == "low")

        risk_score = clamp_0_100(
            12.0
            + high_count * 25.0
            + medium_count * 12.0
            + max(0, len(hops) - 3) * 4.0
            - low_count * 4.0
        )

        draft_readiness = clamp_0_100(
            0.45 * authority_strength
            + 0.40 * coherence_score
            + 0.15 * (100.0 - risk_score)
        )

        notes = "Strong for drafting" if draft_readiness >= 70 else "Use with caution and verify flagged hops"
        return ChainScorecard(
            authority_strength=authority_strength,
            coherence_score=coherence_score,
            risk_score=risk_score,
            draft_readiness=draft_readiness,
            notes=notes,
        )

    def _risk_flags(self, hops: List[HopDetail]) -> List[RiskFlag]:
        flags: List[RiskFlag] = []
        for index, hop in enumerate(hops, start=1):
            if hop.similarity < 0.05:
                flags.append(
                    RiskFlag(
                        severity="high",
                        title="Weak topical bridge",
                        reason=f"Hop {index} has low similarity ({hop.similarity}), indicating a doctrinal leap.",
                        hop_index=index,
                        recommended_check="Read full judgments and verify issue overlap with direct quotes.",
                    )
                )
            elif hop.similarity < 0.2:
                flags.append(
                    RiskFlag(
                        severity="medium",
                        title="Moderate semantic gap",
                        reason=f"Hop {index} similarity is moderate ({hop.similarity}); argument framing must be explicit.",
                        hop_index=index,
                        recommended_check="Add an intermediate authority or strengthen with statutory context.",
                    )
                )

        if len(hops) >= 5:
            flags.append(
                RiskFlag(
                    severity="medium",
                    title="Long chain risk",
                    reason=f"Path spans {len(hops)} hops and may feel attenuated in oral argument.",
                    recommended_check="Prefer shorter alternative chain for core oral submissions.",
                )
            )

        if not flags:
            flags.append(
                RiskFlag(
                    severity="low",
                    title="No major weak link detected",
                    reason="Chain shows acceptable continuity and manageable depth.",
                    recommended_check="Still verify treatment history before filing.",
                )
            )

        return flags

    def _verification_checklist(self, hops: List[HopDetail]) -> List[str]:
        checks: List[str] = [
            "Check treatment history for each authority (followed/distinguished/overruled).",
            "Extract one direct quote per hop supporting your legal proposition.",
            "Confirm court hierarchy and jurisdiction compatibility with your forum.",
        ]
        for idx, hop in enumerate(hops, start=1):
            checks.append(f"Verify hop {idx}: {hop.from_case} -> {hop.to_case} in full judgment text.")
        return checks

    def _sentence_citations(self, source: str, target: str, path: List[str], hops: List[HopDetail], practice_context: str | None) -> List[SentenceCitation]:
        context = practice_context or "the current matter"
        supports_hops = [f"hop:{idx+1}" for idx in range(len(hops))]
        return [
            SentenceCitation(
                sentence_id="S1",
                text=f"The issue is whether authority from {source} extends to {target} in {context}.",
                supports=[source, target],
            ),
            SentenceCitation(
                sentence_id="S2",
                text=f"The proposed chain contains {len(hops)} citation-verified transitions.",
                supports=supports_hops,
            ),
            SentenceCitation(
                sentence_id="S3",
                text=f"Recommended order of reliance is {' -> '.join(path)}.",
                supports=path,
            ),
        ]

    def _draft_blocks(
        self,
        source: str,
        target: str,
        path: List[str],
        context: str,
        draft_length: DraftLength,
    ) -> tuple[str, str, str]:
        chain_text = ' -> '.join(path)
        bridge_text = ' through '.join(path[1:-1]) if len(path) > 2 else path[-1]

        short_neutral = (
            f"In {context}, the proposition in {target} is consistent with authority from {source}. "
            f"The sequence {chain_text} keeps the doctrinal bridge tight for court submissions."
        )
        short_petitioner = (
            f"For petitioner/appellant: The line from {source} {('through ' + bridge_text) if len(path) > 2 else ''} "
            f"supports extending principle into {target} on rights-protective reading."
        )
        short_respondent = (
            f"For respondent: Even accepting the chain from {source}, {target} must be applied narrowly "
            "within factual and statutory constraints of the present record."
        )

        if draft_length == DraftLength.short:
            return short_neutral, short_petitioner, short_respondent

        standard_neutral = (
            f"In {context}, the proposition in {target} is consistent with the authority line beginning at {source}. "
            f"The citation sequence {chain_text} preserves a continuous doctrinal thread suitable for submission framing. "
            "Each transition should be supported with one direct quotation to anchor principle continuity."
        )
        standard_petitioner = (
            f"For petitioner/appellant: The reasoning lineage from {source} through {bridge_text} culminates in {target}, "
            "supporting a rights-consistent interpretation in this matter. "
            "This framing allows the court to adopt relief without doctrinal rupture because each step is citation-backed."
        )
        standard_respondent = (
            f"For respondent: Even if {target} appears aligned with {source}, the chain still allows limiting principles. "
            "The respondent can concede broad doctrine while contesting factual fit, statutory scheme, and remedy scope. "
            "This preserves precedent respect while narrowing present-case application."
        )

        if draft_length == DraftLength.standard:
            return standard_neutral, standard_petitioner, standard_respondent

        long_neutral = (
            f"In {context}, counsel may present {target} as a logical extension of the authority line beginning in {source}. "
            f"The citation sequence {chain_text} demonstrates that the core legal proposition has been carried forward through successive judicial treatment rather than introduced abruptly. "
            "A persuasive written submission should map each hop to a specific holding sentence, then explain how the receiving court translated that holding into the next doctrinal step. "
            "This lets the bench see continuity in principle, continuity in method, and continuity in remedy architecture. "
            "By structuring the argument this way, the submission appears precedent-disciplined rather than policy-driven."
        )
        long_petitioner = (
            f"For petitioner/appellant: Begin from {source} as the anchor authority and walk the court sequentially through {bridge_text} into {target}. "
            "At each step, identify the exact legal test preserved across cases and show how factual distinctions were treated without breaking the rule-line. "
            "Then argue that the present matter falls within the matured doctrine because the same constitutional or statutory value remains operative under comparable institutional constraints. "
            "Close by requesting relief that mirrors the narrowest precedent-supported outcome, which reduces judicial reluctance while preserving claimant protection. "
            "This framing maximizes doctrinal legitimacy and practical grantability."
        )
        long_respondent = (
            f"For respondent: Accept that {source} and its descendants are relevant, but argue that {target} should not be mechanically transplanted to the present record. "
            "Emphasize where doctrinal language was context-bound, where later benches signaled caution, and where statutory structure imposes independent limits. "
            "Use the same chain to show that courts repeatedly conditioned principle application on institutional competence, evidentiary posture, and remedy proportionality. "
            "Invite the bench to preserve precedent integrity by distinguishing rather than overruling, and to adopt a restrained holding tailored to present facts. "
            "This approach positions the respondent as precedent-faithful while still resisting overbroad extension."
        )
        return long_neutral, long_petitioner, long_respondent

    def _build_brief(
        self,
        source: str,
        target: str,
        path: List[str],
        hops: List[HopDetail],
        practice_context: str | None,
        alternatives: List[AlternativePath],
        draft_length: DraftLength,
    ) -> tuple[LawyerBrief, Dict[str, str | float]]:
        context = practice_context or "general litigation"
        issue = f"Whether reasoning anchored in {source} can be applied to {target} for {context}."
        rule = f"A defensible argument must retain citation lineage and doctrinal continuity across {len(hops)} validated hops."
        application = (
            f"The chain {' -> '.join(path)} links the target to established authority with explicit citations and scored coherence."
        )
        conclusion = "Use this chain as primary structure, with flagged hops reinforced through direct judgment extracts."
        suggested_paragraph, petitioner_paragraph, respondent_paragraph = self._draft_blocks(
            source=source,
            target=target,
            path=path,
            context=context,
            draft_length=draft_length,
        )

        authorities_to_read_first = path[: min(4, len(path))]
        disclaimer = "Research aid only. Verify all authorities, paragraph context, and treatment status before legal use."

        brief_data = {
            "issue": issue,
            "rule": rule,
            "application": application,
            "conclusion": conclusion,
            "suggested_paragraph": suggested_paragraph,
        }

        generation_meta: Dict[str, str | float] = {
            "mode": "template",
            "model": "deterministic",
            "latency_ms": 0.0,
            "draft_length": draft_length.value,
        }

        if config.NARRATIVE_MODE.lower() == "hybrid" and draft_length == DraftLength.standard:
            started = time.perf_counter()
            try:
                rewritten = self.narration_client.rewrite_brief(
                    brief=brief_data,
                    context={
                        "source_case": source,
                        "target_case": target,
                        "practice_context": context,
                        "path": " -> ".join(path),
                        "alternative_count": str(len(alternatives)),
                        "draft_length": draft_length.value,
                    },
                )
                brief_data.update({key: value for key, value in rewritten.items() if value})
                generation_meta = {
                    "mode": "hybrid",
                    "model": self.narration_client.deployment or "azure-narration",
                    "latency_ms": round((time.perf_counter() - started) * 1000.0, 3),
                    "draft_length": draft_length.value,
                }
            except Exception:
                generation_meta = {
                    "mode": "template_fallback",
                    "model": "deterministic",
                    "latency_ms": round((time.perf_counter() - started) * 1000.0, 3),
                    "draft_length": draft_length.value,
                }

        brief = LawyerBrief(
            issue=brief_data["issue"],
            rule=brief_data["rule"],
            application=brief_data["application"],
            conclusion=brief_data["conclusion"],
            suggested_paragraph=brief_data["suggested_paragraph"],
            petitioner_paragraph=petitioner_paragraph,
            respondent_paragraph=respondent_paragraph,
            authorities_to_read_first=authorities_to_read_first,
            disclaimer=disclaimer,
        )
        return brief, generation_meta

    def find_path(
        self,
        source_value: str,
        target_value: str,
        algorithm: AlgorithmName,
        alpha: float,
        beta: float,
        max_depth: int,
        practice_context: str | None = None,
        draft_length: DraftLength = DraftLength.standard,
    ) -> PathFindResponse:
        source = self._resolve_case(source_value)
        target = self._resolve_case(target_value)

        if source is None:
            raise ValueError(f"Source case not found: {source_value}")
        if target is None:
            raise ValueError(f"Target case not found: {target_value}")

        selected = self._run_algorithm(source, target, algorithm, alpha, beta, max_depth)

        if selected is None:
            no_brief = LawyerBrief(
                issue=f"No validated citation route found from {source} to {target}.",
                rule="Recommendation requires at least one structurally valid citation path.",
                application="Current constraints returned no reachable route.",
                conclusion="Broaden search and re-run with alternate starting authority.",
                suggested_paragraph="No draft paragraph available because no valid chain exists.",
                petitioner_paragraph="No petitioner draft available.",
                respondent_paragraph="No respondent draft available.",
                authorities_to_read_first=[source, target],
                disclaimer="Research aid only. Verify all authorities before legal use.",
            )
            empty_metrics = PathMetrics(total_cost=0.0, hop_count=0, runtime_ms=0.0, algorithm=algorithm)
            return PathFindResponse(
                path=[],
                hops=[],
                metrics=empty_metrics,
                explanation="No structurally valid citation path exists between the requested cases.",
                recommended_chain=RecommendedChain(
                    source_case=source,
                    target_case=target,
                    path=[],
                    persuasive_reason="No citation-backed chain under current constraints.",
                ),
                chain_scorecard=ChainScorecard(
                    authority_strength=0.0,
                    coherence_score=0.0,
                    risk_score=100.0,
                    draft_readiness=0.0,
                    notes="No valid chain.",
                ),
                lawyer_brief=no_brief,
                verification_checklist=["Change source authority or expand corpus coverage and retry."],
                alternatives=[],
                counter_argument_pack=CounterArgumentPack(
                    likely_opposing_chain=[],
                    opposing_argument="Opposing side can challenge absence of citation lineage.",
                    rebuttal_strategy="Locate nearer controlling authorities before proceeding.",
                ),
                risk_flags=[
                    RiskFlag(
                        severity="high",
                        title="No valid path",
                        reason="Graph traversal could not connect source and target.",
                        recommended_check="Choose a different anchor precedent or wider dataset.",
                    )
                ],
                sentence_citations=[
                    SentenceCitation(
                        sentence_id="S1",
                        text="No citation-backed route was found for the selected query.",
                        supports=[source, target],
                    )
                ],
                generation_meta={"mode": "template", "model": "deterministic", "latency_ms": 0.0},
            )

        candidates: List[CandidatePath] = []
        for algo in [AlgorithmName.bfs, AlgorithmName.bellman_ford, AlgorithmName.floyd]:
            candidate = self._run_algorithm(source, target, algo, alpha, beta, max_depth)
            if candidate is not None:
                candidates.append(candidate)

        unique_candidates = self._dedupe_candidates(candidates)
        alternatives = self._build_alternatives(unique_candidates)
        risk_flags = self._risk_flags(selected.hops)
        verification_checklist = self._verification_checklist(selected.hops)
        sentence_citations = self._sentence_citations(source, target, selected.path, selected.hops, practice_context)
        brief, generation_meta = self._build_brief(source, target, selected.path, selected.hops, practice_context, alternatives, draft_length)
        scorecard = self._chain_scorecard(selected.path, selected.hops, risk_flags)
        counter_pack = self._counter_argument_pack(alternatives, selected.path)

        explanation = (
            f"Built a {selected.metrics.hop_count}-hop chain from {source} to {target} with citation validity and doctrinal coherence."
        )
        persuasive_reason = "This chain offers the best balance of citation continuity, authority strength, and draft readiness."

        return PathFindResponse(
            path=selected.path,
            hops=selected.hops,
            metrics=selected.metrics,
            explanation=explanation,
            recommended_chain=RecommendedChain(
                source_case=source,
                target_case=target,
                path=selected.path,
                persuasive_reason=persuasive_reason,
            ),
            chain_scorecard=scorecard,
            lawyer_brief=brief,
            verification_checklist=verification_checklist,
            alternatives=alternatives,
            counter_argument_pack=counter_pack,
            risk_flags=risk_flags,
            sentence_citations=sentence_citations,
            generation_meta=generation_meta,
        )
