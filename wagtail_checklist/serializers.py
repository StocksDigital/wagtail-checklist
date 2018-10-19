import re

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from wagtail.core.models import Page

from .rules import check_form_rules, check_rules


class PageActions:
    EDIT = 'EDIT'
    CREATE = 'CREATE'


class ChecklistSerializer(serializers.Serializer):
    EDIT_REGEX = r'/pages/(?P<page_id>\d+)/edit/$'
    CREATE_REGEX = r'/pages/add/(?P<app_name>\w+)/(?P<model_name>\w+)/(?P<parent_id>\d+)/$'

    url = serializers.URLField()
    action = serializers.ChoiceField([PageActions.EDIT, PageActions.CREATE])
    page = serializers.JSONField()

    def validate(self, data):
        """
        Ensure that the provided URL is from the Wagtail edit or create views, so that
        we can extract some required information using EDIT_REGEX / CREATE_REGEX
        """
        validated = super().validate(data)
        action = validated['action']
        is_valid_url = (
            (action == PageActions.EDIT and re.search(self.EDIT_REGEX, validated['url'])) or
            (action == PageActions.CREATE and re.search(self.CREATE_REGEX, validated['url']))
        )
        if not is_valid_url:
            raise serializers.ValidationError('Invalid URL for action {}'.format(action))
        return validated

    def create(self, validated_data):
        """
        Construct a Page instance and validate the instance against the built-in Wagtail
        form, as well as any rules that are registered.
        """
        # Use information encoded in the URL to build a page instance.
        if validated_data['action'] == PageActions.EDIT:
            page_class, page, parent_page = self.get_edit_page(validated_data)
        else:
            page_class, page, parent_page = self.get_create_page(validated_data)

        # Construct and validate a model-specific form so that we can add Wagtail's built-in
        # validation to our response.
        edit_handler = page_class.get_edit_handler()
        form_class = edit_handler.get_form_class()
        form = form_class(validated_data['page'], instance=page, parent_page=parent_page)

        # Build a list of Wagtail built-in form errors
        form_rules = check_form_rules(page_class, form)

        # Build a list of custom rules
        error_rules, warning_rules = check_rules(page_class, page, parent_page)

        rule_lists = [
            ('ERROR', form_rules),
            ('ERROR', error_rules),
            ('WARNING', warning_rules)
        ]

        # Build the checklist from the rule lists
        checklist = {}
        for error_type, rule_list in rule_lists:
            for rule in rule_list:
                serialized_rule = {
                    'isValid': rule.is_valid,
                    'hasError': rule.has_error,
                    'type': error_type,
                    'message': rule.message,
                }
                name = rule.name.lower().replace('_', ' ')
                try:
                    checklist[name].append(serialized_rule)
                except (KeyError, AttributeError):
                    checklist[name] = [serialized_rule]

        return {'checklist': checklist}

    def get_edit_page(self, validated_data):
        """
        Construct a Page instance using data the Wagtail editor's 'edit' page.
        Use the Page pk to fetch the instance from the database.
        """
        url_data = re.search(self.EDIT_REGEX, validated_data['url']).groupdict()
        page = Page.objects.get(pk=url_data['page_id']).specific
        content_type = ContentType.objects.get_for_model(page)
        page_class = content_type.model_class()
        parent_page = page.get_parent()
        if not parent_page:
            raise serializers.ValidationError('Page must have a parent')

        return page_class, page, parent_page

    def get_create_page(self, validated_data):
        """
        Construct a Page instance using data the Wagtail editor's 'add' page.
        Use the app name and model name to construct a new Page model.
        """
        url_data = re.search(self.CREATE_REGEX, validated_data['url']).groupdict()
        content_type = ContentType.objects.get_by_natural_key(url_data['app_name'], url_data['model_name'])
        page_class = content_type.model_class()
        parent_page = Page.objects.get(pk=url_data['parent_id']).specific
        page = page_class()
        return page_class, page, parent_page
