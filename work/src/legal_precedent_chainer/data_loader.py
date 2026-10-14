from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from legal_precedent_chainer.models import CaseRecord


class DataValidationError(Exception):
    pass


def load_cases(path: Path) -> Dict[str, CaseRecord]:
    if not path.exists():
        raise FileNotFoundError(f"Cases file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise DataValidationError("Expected top-level JSON array for cases data.")

    cases: Dict[str, CaseRecord] = {}
    for entry in payload:
        record = CaseRecord.model_validate(entry)
        cases[record.id] = record

    if not cases:
        raise DataValidationError("No cases found in data source.")

    return cases
