#coding: utf-8

from xTool.utils.rule import BaseRule


class TriggerRule(BaseRule):
    ALL_SUCCESS = 'all_success'
    ALL_FAILED = 'all_failed'
    ALL_DONE = 'all_done'
    ONE_SUCCESS = 'one_success'
    ONE_FAILED = 'one_failed'
    DUMMY = 'dummy'


class TestTriggerRule:
    def test_is_valid(self):
        rule = TriggerRule()
        actual = rule.is_valid('all_success')
        assert actual == True

        actual = rule.is_valid('not_found')
        assert actual == False


