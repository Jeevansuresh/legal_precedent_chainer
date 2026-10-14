from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Callable, Dict, Iterable, List, Optional, Tuple

import networkx as nx
import numpy as np


@dataclass
class SearchResult:
    path: List[str]
    total_cost: float



def reconstruct_path(parent: Dict[str, Optional[str]], target: str) -> List[str]:
    result = [target]
    current = target
    while parent[current] is not None:
        current = parent[current]
        result.append(current)
    result.reverse()
    return result



def bfs_path(graph: nx.DiGraph, source: str, target: str, max_depth: int = 25) -> Optional[SearchResult]:
    queue = deque([source])
    parent: Dict[str, Optional[str]] = {source: None}
    depth: Dict[str, int] = {source: 0}

    while queue:
        node = queue.popleft()
        if node == target:
            path = reconstruct_path(parent, target)
            return SearchResult(path=path, total_cost=float(len(path) - 1))

        if depth[node] >= max_depth:
            continue

        for neighbor in graph.successors(node):
            if neighbor not in parent:
                parent[neighbor] = node
                depth[neighbor] = depth[node] + 1
                queue.append(neighbor)

    return None


def bellman_ford_path(
    graph: nx.DiGraph,
    source: str,
    target: str,
    edge_cost: Callable[[str, str], float],
) -> Optional[SearchResult]:
    if source not in graph or target not in graph:
        return None

    def weight(u: str, v: str, _: Dict[str, float]) -> float:
        return edge_cost(u, v)

    try:
        path = nx.bellman_ford_path(graph, source, target, weight=weight)
    except (nx.NetworkXNoPath, nx.NodeNotFound, nx.NetworkXUnbounded):
        return None

    total_cost = 0.0
    for i in range(len(path) - 1):
        total_cost += edge_cost(path[i], path[i + 1])

    return SearchResult(path=path, total_cost=total_cost)



def dijkstra_path(
    graph: nx.DiGraph,
    source: str,
    target: str,
    edge_cost: Callable[[str, str], float],
) -> Optional[SearchResult]:
    dist: Dict[str, float] = {source: 0.0}
    parent: Dict[str, Optional[str]] = {source: None}
    pq: List[Tuple[float, str]] = [(0.0, source)]

    while pq:
        cost_u, node = heappop(pq)
        if cost_u > dist.get(node, float("inf")):
            continue

        if node == target:
            return SearchResult(path=reconstruct_path(parent, target), total_cost=cost_u)

        for neighbor in graph.successors(node):
            alt = cost_u + edge_cost(node, neighbor)
            if alt < dist.get(neighbor, float("inf")):
                dist[neighbor] = alt
                parent[neighbor] = node
                heappush(pq, (alt, neighbor))

    return None



def astar_path(
    graph: nx.DiGraph,
    source: str,
    target: str,
    edge_cost: Callable[[str, str], float],
    heuristic: Callable[[str], float],
) -> Optional[SearchResult]:
    open_set: List[Tuple[float, str]] = [(heuristic(source), source)]
    g_score: Dict[str, float] = {source: 0.0}
    parent: Dict[str, Optional[str]] = {source: None}

    while open_set:
        _, node = heappop(open_set)
        if node == target:
            return SearchResult(path=reconstruct_path(parent, target), total_cost=g_score[target])

        for neighbor in graph.successors(node):
            tentative = g_score[node] + edge_cost(node, neighbor)
            if tentative < g_score.get(neighbor, float("inf")):
                parent[neighbor] = node
                g_score[neighbor] = tentative
                f_score = tentative + heuristic(neighbor)
                heappush(open_set, (f_score, neighbor))

    return None



def floyd_warshall_path(
    graph: nx.DiGraph,
    source: str,
    target: str,
    edge_cost: Callable[[str, str], float],
) -> Optional[SearchResult]:
    if source not in graph or target not in graph:
        return None

    nodes = list(graph.nodes())
    if len(nodes) > 300:
        descendants = nx.descendants(graph, source)
        ancestors = nx.ancestors(graph, target)
        candidate_nodes = (descendants & ancestors) | {source, target}

        if not candidate_nodes:
            return None

        subgraph = graph.subgraph(candidate_nodes).copy()
        nodes = list(subgraph.nodes())

        if len(nodes) > 300:
            return None
        graph = subgraph

    index = {node: idx for idx, node in enumerate(nodes)}
    n = len(nodes)

    dist = np.full((n, n), np.inf)
    nxt = [[None for _ in range(n)] for _ in range(n)]

    for i in range(n):
        dist[i, i] = 0.0
        nxt[i][i] = nodes[i]

    for u, v in graph.edges():
        i, j = index[u], index[v]
        cost = edge_cost(u, v)
        if cost < dist[i, j]:
            dist[i, j] = cost
            nxt[i][j] = v

    for k in range(n):
        for i in range(n):
            if np.isinf(dist[i, k]):
                continue
            for j in range(n):
                alt = dist[i, k] + dist[k, j]
                if alt < dist[i, j]:
                    dist[i, j] = alt
                    nxt[i][j] = nxt[i][k]

    if source not in index or target not in index:
        return None

    i, j = index[source], index[target]
    if nxt[i][j] is None or np.isinf(dist[i, j]):
        return None

    path = [source]
    current = source
    while current != target:
        next_node = nxt[index[current]][j]
        if next_node is None:
            return None
        path.append(next_node)
        current = next_node

    return SearchResult(path=path, total_cost=float(dist[i, j]))
