from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel

from wagtail_checklist.rules import dont_check_rule, register_error_rule, register_warning_rule


class BlogPage(Page):
    template = 'page.html'

    body = RichTextField(features=['bold', 'h2'])

    content_panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('body', classname='full'),
    ]


class NewsPage(Page):
    template = 'page.html'

    body = RichTextField(features=['bold', 'h2'])

    content_panels = [
        FieldPanel('title', classname='full title'),
        FieldPanel('body', classname='full'),
    ]


# This is a warning rule, it will:
#   - make the checklist button turn yellow
#   - show an error message in the modal
#   - not block publish
@register_warning_rule(Page, 'title', 'Title should be 10 characters or more.')
def validate_page_title_minimum_length(page, parent):
    """
    Ensure the page title is at least 10 characters long
    """
    return page.title and len(page.title) >= 10


# This is an error rule, it will:
#   - make the checklist button turn red
#   - show an error message in the modal
#   - block publish (via HTML only)
@register_error_rule(Page, 'title', 'Title cannot be longer than 20 characters.')
def validate_page_title_maximum_length(page, parent):
    """
    Ensure the page title is at least 10 characters long
    """
    return page.title and len(page.title) < 21


# You can create rules that only apply to particular Page subclasses.
# For example, this rule will apply to NewsPage and not BlogPage
@register_warning_rule(NewsPage, 'body', 'Body should contain the word \"news\".')
def validate_page_title_minimum_length(page, parent):
    """
    Ensure our news page articles are newsworthy by warning users if there is no "news"
    in the article body.
    """
    return 'news' in page.body.lower()


# You can disable rules as well. This is useful for:
#   - supressing error messages that you don't care about
#   - inheritance of rules (eg. Page > NewsPage)
# Below we:
#   - create a rule that applies to the body of all Page models (ie. NewsPage + BlogPage)
#   - disable that rule for NewsPage
# As a result:
#   - 'mongoose' in the body of a NewsPage will be invalid
#   - 'mongoose' in the body of a BlogPage will be valid
@register_error_rule(Page, 'banned words', 'The body cannot contain the word \"mongoose\".')
def validate_body_banned_words(page, parent):
    """
    Ensure there are no banned words in the page body
    """
    return 'mongoose' not in page.body.lower()

dont_check_rule(BlogPage, 'banned words')
