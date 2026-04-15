from __future__ import annotations

import json
from pathlib import Path

from .schemas import Scenario


def load_scenarios(path: str | Path = "data/scenarios.json") -> list[Scenario]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Scenario.model_validate(item) for item in raw]
