"""Shared crop catalog; longest alias wins, including compounds with suffixes."""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CROPS = json.loads((ROOT/'data/crops.json').read_text(encoding='utf8'))

def entity_text(text):
    return ' '.join(''.join(c if unicodedata.category(c)[0] in 'LM' else ' ' for c in str(text).lower()).split())

ALIASES = sorted([(entity_text(a), c['id']) for c in CROPS for a in
                  [c['english_name'], *c['english_aliases'], *c['romanized_aliases'], *c['telugu_aliases']]],
                 key=lambda x: -len(x[0]))
SUFFIXES = {'ki','ku','lo','lu','s','es','panta','chettu','field','కి','కు','లో','లు','పంట','తో','కి','లోని','లకు','ని'}

def detect_crop(text):
    from ml.slots import detect
    return detect(text,CROPS)
