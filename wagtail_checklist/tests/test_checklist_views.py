import json
from unittest import mock

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from wagtail.core.models import Page

from wagtail_checklist import rules as rule_module
from wagtail_checklist.rules import register_error_rule, register_warning_rule


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


@pytest.fixture()
def user():
    return User.objects.create(username='testy', is_superuser=True)


@pytest.fixture
def parent_page():
    parent_page = Page(title='My cool photo index')
    Page.add_root(instance=parent_page)
    return parent_page


@pytest.fixture
def page():
    parent_page = Page(title='My cool blog index')
    Page.add_root(instance=parent_page)
    page = Page(title='My cool blog')
    parent_page.add_child(instance=page)
    return page


@pytest.fixture
def post_checklist_api(client, user):
    client.force_login(user)
    checklist_url = reverse('wagtail_checklist_api')

    def post(data):
        return client.post(checklist_url, data=json.dumps(data), content_type='application/json')

    return post


@pytest.mark.django_db
def test_validate_edit_page_invalid_url_for_create(post_checklist_api, page):
    response = post_checklist_api({
        # This action / url combo should fail DRF validation
        'url': 'http://example.com/admin/pages/{}/edit/'.format(page.pk),
        'action': 'CREATE',
        'page': {
            'title': page.title + '!',
            'slug': page.slug,
        },
    })
    assert response.status_code == 400


@pytest.mark.django_db
def test_validate_page_invalid_url_for_edit(post_checklist_api, parent_page):
    response = post_checklist_api({
        # This action / url combo should fail DRF validation
        'url': 'http://example.com/admin/pages/add/wagtailcore/page/{}/'.format(parent_page.pk),
        'action': 'EDIT',
        'page': {
            'title': parent_page.title + '!',
            'slug': parent_page.slug,
        },
    })
    assert response.status_code == 400


@pytest.mark.django_db
def test_validate_edit_page_no_rules_no_errors(post_checklist_api, page):
    response = post_checklist_api({
        'url': 'http://example.com/admin/pages/{}/edit/'.format(page.pk),
        'action': 'EDIT',
        'page': {
            'title': page.title + '!',
            'slug': page.slug,
        },
    })
    assert response.status_code == 200
    assert response.data == {'checklist': {}}


@pytest.mark.django_db
def test_validate_create_page_no_rules_no_errors(post_checklist_api, parent_page):
    response = post_checklist_api({
        'url': 'http://example.com/admin/pages/add/wagtailcore/page/{}/'.format(parent_page.pk),
        'action': 'CREATE',
        'page': {
            'title': 'My cool blog',
            'slug': 'my-cool-blog',
        },
    })
    assert response.status_code == 200
    assert response.data == {'checklist': {}}


@pytest.mark.django_db
def test_validate_edit_page_no_rules_builtin_errors(post_checklist_api, page):
    response = post_checklist_api({
        'url': 'http://example.com/admin/pages/{}/edit/'.format(page.pk),
        'action': 'EDIT',
        'page': {
            'title': page.title + '!',
            'slug': '',  # This should fail checklist validation
        },
    })
    assert response.status_code == 200
    assert response.data == {
        'checklist': {
            'slug': [
                {'isValid': False, 'hasError': False, 'message': 'This field is required.', 'type': 'ERROR'}
            ]
        }
    }


@pytest.mark.django_db
def test_validate_create_page_no_rules_builtin_errors(post_checklist_api, parent_page):
    response = post_checklist_api({
        'url': 'http://example.com/admin/pages/add/wagtailcore/page/{}/'.format(parent_page.pk),
        'action': 'CREATE',
        'page': {
            'title': 'My cool blog',
            'slug': '',  # This should fail checklist validation
        },
    })
    assert response.status_code == 200
    assert response.data == {
        'checklist': {
            'slug': [
                {'isValid': False, 'hasError': False, 'message': 'This field is required.', 'type': 'ERROR'}
            ]
        }
    }


@pytest.mark.django_db
@mock.patch('wagtail_checklist.rules.logger')
def test_validate_create_page_with_rules_and_errors(mock_logger, post_checklist_api, parent_page):

    def always_pass(page, parent):
        return True

    def always_fail(page, parent):
        return False

    def always_error(page, parent):
        raise ValueError('Uh oh')

    register_error_rule(Page, 'Title', 'This will always pass')(always_pass)

    register_error_rule(Page, 'Dummy', 'This will always pass')(always_pass)
    register_error_rule(Page, 'Dummy', 'This will always fail')(always_fail)
    register_error_rule(Page, 'Dummy', 'This will always error')(always_error)

    register_warning_rule(Page, 'Dummy', 'This will always pass')(always_pass)
    register_warning_rule(Page, 'Dummy', 'This will always fail')(always_fail)
    register_warning_rule(Page, 'Dummy', 'This will always error')(always_error)

    response = post_checklist_api({
        'url': 'http://example.com/admin/pages/add/wagtailcore/page/{}/'.format(parent_page.pk),
        'action': 'CREATE',
        'page': {
            'title': '',  # This should fail checklist validation
            'slug': 'my-cool-blog',
        },
    })
    assert response.status_code == 200
    actual_data = response.data
    expected_data = {
        'checklist': {
            'title': [
                {'isValid': False, 'hasError': False, 'message': 'This field is required.', 'type': 'ERROR'},
                {'isValid': True, 'hasError': False, 'message': 'This will always pass', 'type': 'ERROR'},
            ],
            'dummy': [
                {'isValid': True, 'hasError': False, 'message': 'This will always pass', 'type': 'ERROR'},
                {'isValid': False, 'hasError': False, 'message': 'This will always fail', 'type': 'ERROR'},
                {'isValid': True, 'hasError': True, 'message': 'This will always error', 'type': 'ERROR'},
                {'isValid': True, 'hasError': False, 'message': 'This will always pass', 'type': 'WARNING'},
                {'isValid': False, 'hasError': False, 'message': 'This will always fail', 'type': 'WARNING'},
                {'isValid': True, 'hasError': True, 'message': 'This will always error', 'type': 'WARNING'},
            ]
        }
    }
    assert actual_data == expected_data
