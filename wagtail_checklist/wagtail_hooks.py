import json

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.urls import reverse
from wagtail.core import hooks


@hooks.register('insert_editor_js')
def editor_js():
    """
    Add custom JS for Wagtail editor admin
    """
    # Load data for checklist app into client
    frontend_data = {
        'API_URL': reverse('wagtail_checklist_api'),
    }
    load_js_data = '<script>var CHECKLIST = JSON.parse(\'{json}\')</script>'.format(
        json=json.dumps(frontend_data)
    )

    # Load JavaScript code into client
    src = static('wagtail_checklist/js/wagtail_checklist.js')
    js_code = '<script type="text/javascript" defer src="{src}"></script>'.format(src=src)
    return load_js_data + js_code
