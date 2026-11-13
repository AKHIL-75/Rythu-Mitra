"""Actual Flask transport over stdio when local TCP is restricted by the runner.

This executes the real API/model and static routes, without fabricated predictions.
It is a test harness only; ordinary users run app.py over HTTP.
"""
import base64
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.vendor')]
from app import app
client=app.test_client()
for line in sys.stdin:
    try:
        q=json.loads(line)
        response=client.open(q['path'],method=q.get('method','GET'),data=q.get('body'),content_type=q.get('content_type'))
        out=dict(id=q['id'],status=response.status_code,content_type=response.content_type,
                 body=base64.b64encode(response.get_data()).decode('ascii'))
    except Exception as e:out=dict(id=q.get('id'),error=str(e))
    print(json.dumps(out),flush=True)
