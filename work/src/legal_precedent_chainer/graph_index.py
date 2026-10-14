from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import networkx as nx
import numpy as np

from legal_precedent_chainer.models import CaseRecord


@dataclass
class BuiltGraph:
    graph: nx.DiGraph
    embeddings: Dict[str, np.ndarray]
    cases: Dict[str, CaseRecord]



def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    denom = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
    if denom == 0.0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)



def build_graph(cases: Dict[str, CaseRecord], embeddings: Dict[str, List[float]]) -> BuiltGraph:
    graph = nx.DiGraph()

    for case_id, case in cases.items():
        graph.add_node(case_id)
        for cited in case.citations:
            if cited in cases:
                graph.add_edge(case_id, cited)

    embedding_np = {case_id: np.array(vector, dtype=np.float64) for case_id, vector in embeddings.items()}

    return BuiltGraph(graph=graph, embeddings=embedding_np, cases=cases)
