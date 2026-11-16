"""Validated, dated official mandi reports for hosts unable to reach the upstream API."""
import json
import math
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta
from ml.prices import SOURCE

REPORT_PATH = Path(__file__).resolve().parents[1] / 'data/mandi_prices.json'
UNIT = 'INR per quintal (as published by the mandi resource)'
FIELDS = ['state','district','market','commodity','variety','grade','arrival_date','min_price','max_price','modal_price']


def now_utc():
    return datetime.now(timezone.utc)


def parse_date(value):
    for fmt in ['%d/%m/%Y', '%Y-%m-%d']:
        try:
            return datetime.strptime(str(value), fmt).date()
        except ValueError:
            pass
    raise ValueError('Invalid reporting date')


def valid_record(row):
    if not isinstance(row, dict):
        return None
    if any(not isinstance(row.get(k), str) or not row[k].strip() for k in ['state','district','market','commodity','arrival_date']):
        return None
    if row['state'].strip().casefold() != 'telangana':
        return None
    try:
        if parse_date(row['arrival_date']) > now_utc().astimezone(timezone(timedelta(hours=5, minutes=30))).date():
            return None
        if row.get('modal_price') is None or isinstance(row.get('modal_price'),bool) or str(row['modal_price']).strip() == '':
            return None
        modal = float(row['modal_price'])
        if not math.isfinite(modal) or modal < 0:
            return None
        result = {k: row.get(k) for k in FIELDS}
        for k in ['min_price','max_price']:
            value = result[k]
            if value is None or value == '':
                result[k] = None
            elif isinstance(value,bool) or not math.isfinite(float(value)) or float(value) < 0:
                return None
        for k in ['variety','grade']:
            if result[k] is not None and not isinstance(result[k],str):
                return None
        for k in ['state','district','market','commodity','arrival_date']:
            result[k] = result[k].strip()
        # No source URL, API key, or unrecognised provider metadata is persisted per row.
        return result
    except (TypeError, ValueError):
        return None


def validate_report(data):
    if not isinstance(data,dict) or data.get('schema_version') != 1 or data.get('source') != SOURCE or data.get('unit') != UNIT:
        raise ValueError('Invalid report metadata')
    fetched = datetime.fromisoformat(data['fetched_at'].replace('Z','+00:00'))
    if fetched.tzinfo is None or fetched > now_utc() + timedelta(minutes=5):
        raise ValueError('Invalid fetch time')
    coverage = data.get('coverage',{})
    if coverage.get('state') != 'Telangana' or coverage.get('complete') is not True:
        raise ValueError('Incomplete report')
    raw = data.get('records')
    if not isinstance(raw,list) or not raw or any(valid_record(r) is None for r in raw):
        raise ValueError('Invalid or empty report records')
    return dict(schema_version=1,source=SOURCE,unit=UNIT,fetched_at=data['fetched_at'],coverage=coverage,records=[valid_record(r) for r in raw])


def save_report(records, received_rows, path=None):
    rows=[r for row in records if (r:=valid_record(row)) is not None]
    if not rows:
        raise ValueError('No complete Telangana price records returned; previous report preserved')
    data = dict(schema_version=1, source=SOURCE, unit=UNIT,
                fetched_at=now_utc().isoformat().replace('+00:00','Z'),
                coverage=dict(state='Telangana', complete=True, received_rows=received_rows,
                              discarded_rows=received_rows-len(rows)), records=rows)
    validate_report(data)
    destination=Path(path or REPORT_PATH)
    destination.parent.mkdir(parents=True,exist_ok=True)
    temporary=None
    try:
        with tempfile.NamedTemporaryFile('w',encoding='utf8',dir=destination.parent,suffix='.tmp',delete=False) as f:
            temporary=f.name
            json.dump(data,f,ensure_ascii=False,indent=2,allow_nan=False)
            f.flush();os.fsync(f.fileno())
        os.replace(temporary,destination)
    finally:
        if temporary and Path(temporary).exists():Path(temporary).unlink()
    return data


def normal(value):
    text=' '.join(str(value).casefold().split())
    # Alternate spellings of the SAME district, not substitution with Warangal.
    return {'hanamkonda':'hanumakonda'}.get(text,text)


def reported_prices(filters,path=None):
    clean={}
    for key in ['state','district','market','commodity']:
        value=filters.get(key,'')
        if not isinstance(value,str) or len(value)>100:
            return {'status':'invalid_filter','records':[], 'message':'Use text filters of at most 100 characters.'},400
        if value.strip():clean[key]=value.strip()
    try:
        file=Path(path or REPORT_PATH)
        if file.stat().st_size>20_000_000:raise ValueError('Report too large')
        data=validate_report(json.loads(file.read_text(encoding='utf8')))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None
    rows=[r for r in data['records'] if all(normal(r.get(k,''))==normal(v) for k,v in clean.items())]
    rows.sort(key=lambda r:parse_date(r['arrival_date']),reverse=True)
    fetched=datetime.fromisoformat(data['fetched_at'].replace('Z','+00:00'))
    old=(now_utc()-fetched)>timedelta(hours=24)
    message=('Saved official mandi report. These are reported rates, not a live lookup. Check each reporting date.' if rows else
             'No matching rate is present in the saved official report. This does not mean the price is zero. Try broader filters.')
    if old:message+=' The saved report has not been refreshed in the past 24 hours.'
    return dict(status='ok' if rows else 'no_records', records=rows, source=SOURCE, unit=UNIT,
                agmarknet='https://agmarknet.gov.in/', fetched_at=data['fetched_at'],
                source_mode='saved_report', report_outdated=old, cached=False, filters=clean,
                message=message, reporting_dates=sorted({r['arrival_date'] for r in rows})),200


def get_prices(filters):
    from ml.prices import fetch_prices
    # Vercel's upstream connection has been tested and consistently times out.
    # Serve a published report immediately; do not spend 25 seconds on every click.
    if os.environ.get('VERCEL') == '1':
        saved=reported_prices(filters)
        if saved is not None:return saved
        return dict(status='report_unavailable',records=[],source=SOURCE,unit=UNIT,
                    agmarknet='https://agmarknet.gov.in/',
                    message='An official mandi report is not available yet. Please check Agmarknet. No rate is shown.'),503
    live,status=fetch_prices(filters)
    if status>=500 or live.get('status')=='not_configured':
        saved=reported_prices(filters)
        if saved is not None:return saved
    return live,status
