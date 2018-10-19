from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel


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
