"""Temporary, authenticated provider probes. No query URLs or credentials are returned."""
import json
import logging
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from ml import prices

LOGGER = logging.getLogger(__name__)
STAGES = {"minimal", "state", "filtered"}


def probe(stage, filters, opener=None):
    if not isinstance(stage, str) or stage not in STAGES:
        return {"status": "invalid_stage"}, 400
    if not isinstance(filters, dict):
        return {"status": "invalid_filters"}, 400
    clean = {}
    for field in ["state", "district", "market", "commodity"]:
        value = filters.get(field, "")
        if not isinstance(value, str) or len(value) > 100:
            return {"status": "invalid_filters"}, 400
        if value.strip():
            clean[field] = value.strip()
    key = os.environ.get("DATA_GOV_IN_API_KEY", "").strip()
    if not key:
        return {"stage": stage, "status": "not_configured"}, 200
    selected = {} if stage == "minimal" else {"state": clean.get("state", "Telangana")}
    if stage == "filtered":
        selected.update(clean)
    params = {"api-key": key, "format": "json", "limit": 1,
              **{f"filters[{'state.keyword' if k == 'state' else k}]": v for k, v in selected.items()}}
    result = {"stage": stage, "limit": 1, "filter_fields": sorted(selected)}
    started = time.monotonic()
    try:
        with (opener or prices._open_provider)(prices.RESOURCE + "?" + urlencode(params), timeout=8) as response:
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("oversize")
        data = json.loads(raw)
        if not isinstance(data, dict) or not isinstance(data.get("records"), list):
            raise ValueError("invalid payload")
        result.update(status="ok", upstream_http_status=200, record_count=len(data["records"]))
    except HTTPError as error:
        result.update(status="authentication_failed" if error.code in (401, 403) else
                      "rate_limited" if error.code == 429 else "upstream_http_error",
                      upstream_http_status=error.code)
    except TimeoutError:
        result.update(status="timeout")
    except URLError:
        result.update(status="connection_failed")
    except (ValueError, TypeError):
        result.update(status="invalid_response")
    except Exception:
        result.update(status="request_failed")
    result["elapsed_seconds"] = round(time.monotonic() - started, 2)
    LOGGER.warning("Mandi diagnostic stage=%s status=%s elapsed_seconds=%s http_status=%s",
                   stage, result["status"], result["elapsed_seconds"], result.get("upstream_http_status"))
    return result, 200
