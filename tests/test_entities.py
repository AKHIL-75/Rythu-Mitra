import pytest
from ml.entities import CROPS,detect_crop

CASES=[(c['id'],a) for c in CROPS for a in [c['english_name'],*c['english_aliases'],*c['romanized_aliases'],*c['telugu_aliases']]]

@pytest.mark.parametrize('expected,alias',CASES)
def test_every_alias(expected,alias):
    assert detect_crop(alias)==(None if expected=="turmeric" and alias.lower()!="turmeric" else expected)
    assert detect_crop(alias+' ki')==expected
    assert detect_crop(alias+' lo')==expected
    assert detect_crop(alias+' chettu')==expected
    assert detect_crop(alias+' panta')==expected

@pytest.mark.parametrize('query,expected',[('పత్తికి','cotton'),('టమాటాలో','tomato'),('tomatoes','tomato'),('mokkajonna metha','maize_fodder'),('pachi mirapa','green_chilli'),('sweet potato','sweet_potato'),('field bean','field_bean'),('broad beans','broad_beans')])
def test_suffixes_and_longest_match(query,expected):
    assert detect_crop(query)==expected

def test_colour_ambiguity_and_compound_plural():
    assert detect_crop('patti aakulu pasupu avuthunnayi')=='cotton'
    assert detect_crop('ఆకులు పసుపు రంగులో ఉన్నాయి') is None
    assert detect_crop('green chillies ki')=='green_chilli'
