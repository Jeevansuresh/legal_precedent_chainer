# Legal Precedent Chainer (MVP)

FastAPI project to find a legally coherent citation chain between two cases using:
- Structural validity (real citation edges)
- Semantic coherence (embedding similarity)

## Algorithms implemented
- `bfs` (unweighted baseline)
- `dijkstra` (weighted coherent search)
- `astar` (weighted search with heuristic)
- `floyd` (all-pairs shortest path on manageable graph sizes)

## Project layout
- `src/legal_precedent_chainer/` core app and algorithms
- `data/processed/cases_seed.json` synthetic India-leaning seed dataset
- `src/legal_precedent_chainer/ingest_public.py` optional public data fetch starter

## Setup
```powershell
cd work
python -m pip install -e .
```

## Run API
```powershell
cd work
python -m uvicorn legal_precedent_chainer.main:app --reload
```

## API
### Health
`GET /health`

### Case lookup
`GET /case/{case_id}`

### Path search
`POST /path/find`

Example payload:
```json
{
  "source_case_id": "IN-SC-2023-SAME-SEX-MARRIAGE",
  "target_case_id": "IN-SC-1950-AKM-GOPALAN",
  "algorithm": "dijkstra",
  "alpha": 1.0,
  "beta": 2.0,
  "max_depth": 25
}
```

## Azure embeddings (optional but recommended)
Set environment variables:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`

If Azure config is missing/unavailable, the app falls back to deterministic local vectors so demos still run offline.

## Tests
```powershell
cd work
pytest -q
```


## Lawyer-first features
- `POST /path/find` now returns recommended chain, lawyer brief, verification checklist, alternatives, risk flags, and sentence-level citation trace.
- `POST /argument/export` returns memo-ready markdown plus full structured payload.
- UI at `/` defaults to lawyer workflow; technical controls are under Technical mode.


## Azure narration model (optional)
For lawyer-brief rewriting, set either:
- `AZURE_OPENAI_RESPONSES_URL` (e.g. `https://<resource>.services.ai.azure.com/openai/v1/responses`)
- `AZURE_OPENAI_CHAT_DEPLOYMENT` (your deployment/model name, e.g. `gpt-4.1-mini`)
- `AZURE_OPENAI_API_KEY`

If not set (or request fails), narrative generation falls back to deterministic template mode.


## Demo enhancements (lawyer-facing)
- Natural-language question input with `/api/query/suggest` to infer source/target cases.
- Hop evidence includes per-hop snippets and explanation (`why_hop`).
- Chain quality scorecard (authority strength, coherence, risk, draft readiness).
- Counter-argument pack (likely opposing chain + rebuttal strategy).
- Draft blocks for neutral, petitioner/appellant, and respondent usage.
- Export memo includes scorecard, draft blocks, risks, and counter-argument section.
- Technical controls remain optional under Technical mode.
