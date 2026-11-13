from ml.preprocess import normalize, script_type

def test_telugu_marks_preserved():
    assert normalize('పంటకు నీరు ఎప్పుడు?')=='పంటకు నీరు ఎప్పుడు'

def test_urls_digits_punctuation():
    assert normalize('VARI! 123 https://test.invalid/path, ki... నీరు?')=='vari ki నీరు'

def test_variants():
    assert normalize('varri eruvulu neellu tamota')=='vari eruvu neeru tamata'

def test_script_labels():
    assert script_type('పంటకు నీరు')=='telugu'
    assert script_type('పత్తి fertilizer')=='mixed'
    assert script_type('naaku vari ki neeru')=='romanized'
    assert script_type('irrigate my rice field')=='english'
