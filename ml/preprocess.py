"""NFC and Unicode-category filtering preserve Telugu vowel/combining marks.

No stopwords are removed: ki, em and ela carry useful question context.
Numbers/URLs are deliberately removed; entities and amounts are not predictions.
"""
import re
import unicodedata

VARIANTS = {'varri':'vari', 'eruvulu':'eruvu', 'neellu':'neeru',
            'neelllu':'neeru', 'tamota':'tamata', 'tamato':'tamata',
            'fertiliser':'fertilizer', 'vathavaranam':'vatavaranam',
            'vaana':'vana', 'thegulu':'tegulu', 'purugulu':'purugu'}

def normalize(text):
    text = unicodedata.normalize('NFC', str(text)).lower()
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = ''.join(c if unicodedata.category(c)[0] in 'LM' or c.isspace() else ' ' for c in text)
    return ' '.join(VARIANTS.get(w, w) for w in text.split())

def script_type(text):
    te = bool(re.search(r'[\u0c00-\u0c7f]', text))
    latin = bool(re.search(r'[a-zA-Z]', text))
    if te:
        return 'mixed' if latin else 'telugu'
    # Language cannot be reliably inferred from script alone. Document heuristic.
    roman = {'naaku','naku','na','ki','ku','lo','em','ela','entha','cheyali','veyali',
             'undi','eppudu','pettali','neeru','neellu','eruvu','eruvulu','repu',
             'varsham','padutunda','cheppandi','kavali','panta','polam','dharalu'}
    return 'romanized' if set(normalize(text).split()) & roman else 'english'
