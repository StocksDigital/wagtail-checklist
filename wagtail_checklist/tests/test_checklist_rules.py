from unittest import mock

import pytest
from wagtail.core.models import Page

from wagtail_checklist import rules as rule_module
from wagtail_checklist.rules import (Rule, RuleRegistrationError, check_form_rules, check_rules, dont_check_rule,
                                     get_ignored_rules, get_rules, register_error_rule, register_rule,
                                     register_warning_rule)


def setup_function(function):
    # Reset the global rule stores
    rule_module.error_rules_registry = {}
    rule_module.warning_rules_registry = {}
    rule_module.ignored_rules_registry = {}


def teardown_function(function):
    # Reset the global rule stores
    rule_module.error_rules_registry = {}
    rule_module.warning_rules_registry = {}
    rule_module.ignored_rules_registry = {}


def test_registry_validation():
    """Ensure the registry functions validate the rule data"""
    registry = {}

    with pytest.raises(RuleRegistrationError):
        register_rule(registry, NotPage, 'fail', 'This should fail')(dummy_func)

    # No name should fail
    with pytest.raises(RuleRegistrationError):
        register_rule(registry, Page, '', 'This should fail')(dummy_func)

    # No message should fail
    with pytest.raises(RuleRegistrationError):
        register_rule(registry, Page, 'fail', '')(dummy_func)

    # Bad function parameter should fail
    with pytest.raises(RuleRegistrationError):
        register_rule(registry, Page, 'fail', 'This should fail')('')

    # This should work
    register_rule(registry, Page, 'work', 'This should work')(dummy_func)


def test_ignore_rule_validation():
    """Ensure the ignore rule functions validates input arguments"""
    with pytest.raises(RuleRegistrationError):
        dont_check_rule(NotPage, 'fail')

    # No name should fail
    with pytest.raises(RuleRegistrationError):
        dont_check_rule(Page, '')

    # This should work
    dont_check_rule(Page, 'work')


def test_register_ignore_rule_populates_registry():
    """Ignoring a rule should populate the ignore registry"""
    dont_check_rule(Page, 'work')
    dont_check_rule(Page, 'play')
    rule_name_set = rule_module.ignored_rules_registry[Page]
    assert 'work' in rule_name_set
    assert 'play' in rule_name_set


def test_register_error_rule_populates_registry():
    """Registering an error rule should populate the error registry"""
    register_error_rule(Page, 'work', 'This should work')(dummy_func)
    register_error_rule(Page, 'work', 'This should also work')(dummy_func)

    actual_rule = rule_module.error_rules_registry[Page][0]
    expected_rule = Rule(dummy_func, 'work', 'This should work')
    assert_rule_equal(actual_rule, expected_rule)

    actual_rule = rule_module.error_rules_registry[Page][1]
    expected_rule = Rule(dummy_func, 'work', 'This should also work')
    assert_rule_equal(actual_rule, expected_rule)


def test_register_warning_rule_populates_registry():
    """Registering a warning rule should populate the warning registry"""
    rule_module.warning_rules_registry = {}
    register_warning_rule(Page, 'work', 'This should work')(dummy_func)
    register_warning_rule(Page, 'work', 'This should also work')(dummy_func)

    actual_rule = rule_module.warning_rules_registry[Page][0]
    expected_rule = Rule(dummy_func, 'work', 'This should work')
    assert_rule_equal(actual_rule, expected_rule)

    actual_rule = rule_module.warning_rules_registry[Page][1]
    expected_rule = Rule(dummy_func, 'work', 'This should also work')
    assert_rule_equal(actual_rule, expected_rule)


def test_get_ignored_rules():
    dont_check_rule(Page, 'how')
    dont_check_rule(Page, 'about')
    dont_check_rule(Page, 'this')
    ignored_rules = get_ignored_rules(Page)
    assert 'how' in ignored_rules
    assert 'about' in ignored_rules
    assert 'this' in ignored_rules


def test_get_ignored_rules_checks_super_class():
    """
    Ensure `get_ignored_rules` fetches ignored rules for super classes.
    """
    class Mammal:
        pass

    class Dog(Mammal):
        pass

    class Cat(Mammal):
        pass

    rule_module.ignored_rules_registry = {}
    rule_module.ignored_rules_registry[Mammal] = set(['blood'])
    rule_module.ignored_rules_registry[Dog] = set(['snout', 'tail'])
    rule_module.ignored_rules_registry[Cat] = set(['hair', 'claws'])

    ignored_rules = get_ignored_rules(Dog)
    assert 'blood' in ignored_rules
    assert 'snout' in ignored_rules
    assert 'tail' in ignored_rules
    assert 'hair' not in ignored_rules
    assert 'claws' not in ignored_rules


def test_get_rules():
    """
    Ensure that when we register a rule we then get it back from `get_rules`.
    """
    registry = {}
    dont_check_rule(Page, 'play')
    register_rule(registry, Page, 'work', 'This should work')(dummy_func)
    register_rule(registry, Page, 'work', 'This should also work')(other_dummy_func)
    register_rule(registry, Page, 'play', 'This should be ignored')(dummy_func)
    register_rule(registry, Page, 'success', 'This should succeed')(dummy_func)
    rules_for_page = get_rules(Page, registry)

    assert_rule_equal(rules_for_page[0], Rule(dummy_func, 'work', 'This should work'))
    assert_rule_equal(rules_for_page[1], Rule(other_dummy_func, 'work', 'This should also work'))
    assert_rule_equal(rules_for_page[2], Rule(dummy_func, 'success', 'This should succeed'))


def test_get_rules_checks_super_class():
    """
    Ensure `get_rules` fetches rules for super classes.
    """
    class Mammal:
        pass

    class Dog(Mammal):
        pass

    class Cat(Mammal):
        pass

    mammal_rule = Rule(dummy_func, 'blood', 'Blood should be warm.')
    dog_rule = Rule(dummy_func, 'snout', 'Snout should be shiny.')
    cat_rule = Rule(dummy_func, 'hair', 'Irritating to eyes.')

    registry = {}
    registry[Mammal] = [mammal_rule]
    registry[Dog] = [dog_rule]
    registry[Cat] = [cat_rule]

    dog_rules = get_rules(Dog, registry)
    assert mammal_rule in dog_rules
    assert dog_rule in dog_rules
    assert cat_rule not in dog_rules


@mock.patch('wagtail_checklist.rules.logger')
def test_check_rules(mock_logger):
    """
    Ensure that the rule checker produces correct results
    """
    dont_check_rule(Page, 'ignored')

    @register_error_rule(Page, 'ignored', 'This should be ignored')
    def validate_foo_fails(page, parent):
        return False

    @register_error_rule(Page, 'foo', 'Foo should be positive')
    def validate_foo_positive(page, parent):
        if page.foo > 3:
            raise ValueError('Uh oh')
        return page.foo > 0

    @register_warning_rule(Page, 'foo', 'Foo should be greater than 2')
    def validate_foo_large(page, parent):
        return page.foo > 2

    page = mock.Mock()
    parent = mock.Mock()
    page.foo = 0
    error_results, warning_results = check_rules(Page, page, parent)
    assert not error_results[0].is_valid
    assert not error_results[0].has_error
    assert not warning_results[0].is_valid
    assert not warning_results[0].has_error

    page.foo = 1
    error_results, warning_results = check_rules(Page, page, parent)
    assert error_results[0].is_valid
    assert not error_results[0].has_error
    assert not warning_results[0].is_valid
    assert not warning_results[0].has_error

    page.foo = 3
    error_results, warning_results = check_rules(Page, page, parent)
    assert error_results[0].is_valid
    assert not error_results[0].has_error
    assert warning_results[0].is_valid
    assert not warning_results[0].has_error

    page.foo = 4
    error_results, warning_results = check_rules(Page, page, parent)
    assert error_results[0].is_valid
    assert error_results[0].has_error
    assert warning_results[0].is_valid
    assert not warning_results[0].has_error


def test_check_form_rules():
    dont_check_rule(Page, 'ignored')
    form = mock.Mock()
    form.errors = {
        'ignored': [
            'This error should be ignored',
        ],
        'title': [
            'This field is required.',
            'This field is too long.',
        ],
        'slug': [
            'This field is required.',
        ],
    }

    form_results = check_form_rules(Page, form)
    form.is_valid.call_count == 1
    assert set([(r.func, r.name, r.message, r.is_valid, r.has_error) for r in form_results]) == set([
        (None, 'title', 'This field is required.', False, False),
        (None, 'title', 'This field is too long.', False, False),
        (None, 'slug', 'This field is required.', False, False),
    ])


class NotPage:
    """A class that is not a subclass of Page"""
    pass


def dummy_func(page, parent):
    """Dummy rule function, used for testing"""
    return True


def other_dummy_func(page, parent):
    """Dummy rule function, used for testing"""
    return True


def assert_rule_equal(actual_rule, expected_rule):
    """
    Helper to compare two Rule objects
    """
    assert actual_rule.func == expected_rule.func
    assert actual_rule.name == expected_rule.name
    assert actual_rule.message == expected_rule.message
    assert actual_rule.has_error == expected_rule.has_error
    assert actual_rule.is_valid == expected_rule.is_valid
