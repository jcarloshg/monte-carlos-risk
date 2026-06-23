from __future__ import annotations

import json

MOCK_DATA_DESCRIPTOR_STUB: dict[str, object] = {
    "provider": "mock",
    "version": "0.1.0-stub",
    "tickers": [],
    "date_range": {"start": None, "end": None},
    "frequency": "daily",
}


def describe_mock_data() -> None:
    print(json.dumps(MOCK_DATA_DESCRIPTOR_STUB, sort_keys=True))
