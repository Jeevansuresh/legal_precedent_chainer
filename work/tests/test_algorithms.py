from legal_precedent_chainer.algorithms import astar_path, bfs_path, dijkstra_path, floyd_warshall_path
from legal_precedent_chainer.data_loader import load_cases
from legal_precedent_chainer.embeddings import EmbeddingProvider
from legal_precedent_chainer.graph_index import build_graph


def _fixture_graph():
    cases = load_cases(__import__("pathlib").Path("data/processed/cases_seed.json"))
    provider = EmbeddingProvider()
    case_ids = list(cases.keys())
    vectors = provider.embed_many([cases[i].summary for i in case_ids])
    built = build_graph(cases, {k: v for k, v in zip(case_ids, vectors)})
    return built


def _edge_cost(built, alpha=1.0, beta=2.0):
    from legal_precedent_chainer.graph_index import cosine_similarity

    def inner(a, b):
        return alpha + beta * (1.0 - cosine_similarity(built.embeddings[a], built.embeddings[b]))

    return inner


def test_bfs_finds_path_with_valid_edges():
    built = _fixture_graph()
    source = "IN-SC-2023-SAME-SEX-MARRIAGE"
    target = "IN-SC-1950-AKM-GOPALAN"

    result = bfs_path(built.graph, source, target, max_depth=12)
    assert result is not None
    for i in range(len(result.path) - 1):
        assert built.graph.has_edge(result.path[i], result.path[i + 1])


def test_no_path_returns_none():
    built = _fixture_graph()
    source = "IN-SC-1950-AKM-GOPALAN"
    target = "IN-SC-2023-SAME-SEX-MARRIAGE"
    assert bfs_path(built.graph, source, target, max_depth=12) is None


def test_dijkstra_and_astar_costs_match():
    built = _fixture_graph()
    source = "IN-SC-2023-SAME-SEX-MARRIAGE"
    target = "IN-SC-1950-AKM-GOPALAN"
    edge_cost = _edge_cost(built)

    dijkstra = dijkstra_path(built.graph, source, target, edge_cost=edge_cost)
    astar = astar_path(
        built.graph,
        source,
        target,
        edge_cost=edge_cost,
        heuristic=lambda node: 0.0,
    )

    assert dijkstra is not None
    assert astar is not None
    assert round(dijkstra.total_cost, 6) == round(astar.total_cost, 6)


def test_floyd_matches_dijkstra_cost_on_sample():
    built = _fixture_graph()
    source = "IN-SC-2018-NAVTEJ"
    target = "IN-SC-1950-AKM-GOPALAN"
    edge_cost = _edge_cost(built)

    dijkstra = dijkstra_path(built.graph, source, target, edge_cost=edge_cost)
    floyd = floyd_warshall_path(built.graph, source, target, edge_cost=edge_cost)

    assert dijkstra is not None
    assert floyd is not None
    assert round(dijkstra.total_cost, 6) == round(floyd.total_cost, 6)
