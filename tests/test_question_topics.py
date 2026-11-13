import json
from pathlib import Path
import pytest
from ml.slots import extract_slots, route_intent

CASES = json.loads((Path(__file__).parent / 'question_cases.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['topic'] + '-' + case['q'][:15])
def test_requested_question_language_and_topic(case):
    slots = extract_slots(case['q'])
    routed = route_intent(case['q'], 'out_of_scope', .1, .01)
    assert routed['intent'] == case['intent']
    assert not routed['clarify']
    for key in ['crop', 'location', 'question_topic']:
        if key in case:
            assert slots[key] == case[key]


def test_equipment_needs_a_machine_and_nonfarm_guard_wins():
    assert route_intent('rent a house', 'out_of_scope', .1, .01)['intent'] == 'out_of_scope'
    assert route_intent('java code to rent a paddy harvester', 'other_agri', .9, .5)['intent'] == 'out_of_scope'


def test_turmeric_price_does_not_confuse_yellow_leaves():
    assert extract_slots('వరంగల్ లో పసుపు ధర ఎంత')['crop'] == 'turmeric'
    assert extract_slots('paddy leaves pasupu rangu')['crop'] == 'paddy'
