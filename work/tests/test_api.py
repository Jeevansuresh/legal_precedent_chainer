from fastapi.testclient import TestClient

from legal_precedent_chainer.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_homepage_available() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Build My Argument" in response.text


def test_case_lookup() -> None:
    response = client.get("/case/IN-SC-2017-PUTTASWAMY")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "IN-SC-2017-PUTTASWAMY"
    assert payload["year"] == 2017


def test_cases_list_available() -> None:
    response = client.get("/api/cases")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert any(item["id"] == "IN-SC-2017-PUTTASWAMY" for item in payload)
    assert "court" in payload[0]


def test_dataset_stats_available() -> None:
    response = client.get("/api/stats")
    assert response.status_code == 200
    payload = response.json()
    assert payload["case_count"] >= 1
    assert payload["citation_edge_count"] >= 1


def test_query_suggestion_endpoint() -> None:
    response = client.post(
        "/api/query/suggest",
        json={
            "question": "Does privacy support marriage equality?",
            "practice_context": "Constitutional law",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["inferred_source_case"]
    assert payload["inferred_target_case"]


def test_path_find_lawyer_fields_present() -> None:
    response = client.post(
        "/path/find",
        json={
            "source_case_id": "IN-SC-2023-SAME-SEX-MARRIAGE",
            "target_case_id": "IN-SC-1950-AKM-GOPALAN",
            "practice_context": "Constitutional law",
            "algorithm": "dijkstra",
            "alpha": 1.0,
            "beta": 2.0,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["recommended_chain"]["path"][0] == "IN-SC-2023-SAME-SEX-MARRIAGE"
    assert payload["lawyer_brief"]["issue"]
    assert payload["chain_scorecard"]["authority_strength"] >= 0
    assert payload["counter_argument_pack"]["rebuttal_strategy"]
    assert payload["verification_checklist"]
    assert payload["alternatives"]
    assert payload["risk_flags"]
    assert payload["sentence_citations"]
    assert payload["generation_meta"]["mode"] in {"template", "hybrid", "template_fallback"}
    assert "from_summary_snippet" in payload["hops"][0]


def test_path_find_can_infer_from_question() -> None:
    response = client.post(
        "/path/find",
        json={
            "user_question": "Does privacy doctrine support equality jurisprudence?",
            "practice_context": "Constitutional law",
            "algorithm": "dijkstra",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["recommended_chain"]["path"]


def test_argument_export_endpoint() -> None:
    response = client.post(
        "/argument/export",
        json={
            "source_case_id": "IN-SC-2023-SAME-SEX-MARRIAGE",
            "target_case_id": "IN-SC-1950-AKM-GOPALAN",
            "practice_context": "Constitutional law",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["memo_markdown"].startswith("# Argument Memo")
    assert "Chain Quality Scorecard" in payload["memo_markdown"]
    assert payload["payload"]["lawyer_brief"]["disclaimer"]
