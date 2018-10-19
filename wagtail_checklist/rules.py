"""
Checklist rules engine.

This module provides methods to add or remove validations from the checklist:
  - register_error_rule
  - register_warning_rule
  - dont_check_rule

It also provides means to validate a Page model against the registered rules:
  - check_rules
  - check_form_rules

"""
import logging
from copy import deepcopy

from wagtail.core.models import Page

logger = logging.getLogger(__name__)


# These registries that contain all registered Rules
error_rules_registry = {
    # SomePageModel: [
    #   <Rule for name: 'Name must be 12 characters or less'>,
    #   <Rule for name: 'Name must not contain spaces'>,
    #   <Rule for main image: 'An image is required'>,
    # ],
    # SomeOtherPageModel: [
    #   <Rule for cube size: 'Width and height cannot exceed a total of 12m'>,
    # ],
}
warning_rules_registry = {
    # SomeOtherPageModel: [
    #   <Rule for cube volume: 'Volume should be greater than 6m^3'>,
    # ],
}
ignored_rules_registry = {
    # SomePageModel: {'title', 'slug'},
    # SomeOtherPageModel: {'tags', 'slug'},
}


class Rule:
    """
    A validation rule which is run on a Page instance.
    """
    def __init__(self, func, name, message):
        self.func = func
        self.name = name
        self.message = message
        self.has_error = False
        self.is_valid = False

    def check(self, page_instance, page_parent):
        try:
            self.is_valid = self.func(page_instance, page_parent)
        except Exception:
            # We catch all exceptions here because we are executing user defined code.
            # We log the exception for visibility and flag it to the user in the client side UI.
            logger.exception('Exception while checking rule %s - %s', self.name, self.message)
            self.is_valid = True
            self.has_error = True

    def __str__(self):
        return '<Rule for {}: \'{}\'>'.format(self.name, self.message)

    def __repr__(self):
        return self.__str__()


def register_error_rule(page_class, rule_name, rule_message):
    """
    A decorator which adds the wrapped function to the list of error rules
    """
    return register_rule(error_rules_registry, page_class, rule_name, rule_message)


def register_warning_rule(page_class, rule_name, rule_message):
    """
    A decorator which adds the wrapped function to the list of warning rules
    """
    return register_rule(warning_rules_registry, page_class, rule_name, rule_message)


def register_rule(registry, page_class, rule_name, rule_message):
    """
    Adds the wrapped function to the supplied registry.

    Wrapped function API is:
        args:
            - page instance <page_class>
            - page parent <Page>
        returns: is_valid <bool>
    """
    if not rule_name:
        raise RuleRegistrationError('Failed to register rule - a name is required')

    if not rule_message:
        raise RuleRegistrationError('Failed to register rule {} - a message is required'.format(rule_name))

    if not issubclass(page_class, Page):
        msg = 'Failure to register rule {} - "{}", since {} is not a subclass of Page'
        raise RuleRegistrationError(msg.format(rule_name, rule_message, page_class))

    def wrapper(func):
        type_name = type(func).__name__
        if type_name != 'function':
            msg = 'Wrapped validation function must be of type "function", not {}.'.format(type_name)
            raise RuleRegistrationError(msg)

        registered_rule = Rule(func, rule_name, rule_message)
        try:
            registry[page_class].append(registered_rule)
        except (KeyError, AttributeError):
            registry[page_class] = [registered_rule]

    return wrapper


def dont_check_rule(page_class, rule_name):
    """
    Add the rule name to the set of ignored rules for the given Page class.
    """
    if not rule_name:
        raise RuleRegistrationError('Failed to ignore rule - a name is required')

    if not issubclass(page_class, Page):
        msg = 'Failure to ignore rule {}, since {} is not a subclass of Page'
        raise RuleRegistrationError(msg.format(rule_name, page_class))

    try:
        ignored_rules_registry[page_class].add(rule_name)
    except (KeyError, AttributeError):
        ignored_rules_registry[page_class] = {rule_name}


def get_ignored_rules(page_class):
    """
    Get the set of ignored rules names for a given page class
    """
    ignored_rules = set()
    for registered_page_class in ignored_rules_registry.keys():
        if not issubclass(page_class, registered_page_class):
            continue

        ignored_rules |= ignored_rules_registry[registered_page_class]

    return ignored_rules


def get_rules(page_class, registry):
    """
    Returns a list of all Rules for `page_class` from a given registry
    """
    rules = []
    ignored_rules = get_ignored_rules(page_class)
    for registered_page_class in registry.keys():
        if not issubclass(page_class, registered_page_class):
            continue

        for rule in registry[registered_page_class]:
            if rule.name in ignored_rules:
                continue

            rules.append(rule)

    return rules


def check_form_rules(page_class, form):
    """
    Returns a list of all failed Rules from a Wagtail `Page` form.
    """
    form.is_valid()
    ignored_rules = get_ignored_rules(page_class)
    rules = []
    for field_name, messages in form.errors.items():
        if field_name in ignored_rules:
            continue

        for message in messages:
            rule = Rule(None, field_name, message)
            rule.is_valid = False
            rules.append(rule)

    return rules


def check_rules(page_class, page_instance, page_parent):
    """
    Checks the Page instance `page_instance` against all registered rules for `page_class`.
    Returns a tuple of checked error and warning Rules.
    """
    error_rules = get_rules(page_class, error_rules_registry)
    warning_rules = get_rules(page_class, warning_rules_registry)

    for rule in error_rules:
        rule.check(deepcopy(page_instance), deepcopy(page_parent))

    for rule in warning_rules:
        rule.check(deepcopy(page_instance), deepcopy(page_parent))

    return error_rules, warning_rules


class RuleRegistrationError(Exception):
    """
    Thrown when a rule fails to register
    """
    pass
