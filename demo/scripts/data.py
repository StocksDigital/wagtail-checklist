from django.contrib.auth.models import User
from wagtail.core.models import Site, Page

from demo.models import BlogPage, NewsPage

Site.objects.all().delete()
Page.objects.all().delete()
User.objects.all().delete()

admin = User.objects.create(
    **{
        "password": "pbkdf2_sha256$100000$zDoltk5zVX2x$2WovHsoOPtFS6xFbwFoSUwQqNP4mnpfYMY9I7k5UsU0=",
        "is_superuser": True,
        "username": "admin",
        "is_staff": True,
        "is_active": True,
    }
)

root_page = Page(title='Root Page')
Page.add_root(instance=root_page)

blog_page = BlogPage(**{
    "title": "Blog Page",
    "slug": "blog-page",
    "live": True,
    "has_unpublished_changes": False,
    "url_path": "/blog/",
    "owner": admin,
    "first_published_at": "2018-08-28T04:30:35.450Z",
    "last_published_at": "2018-08-28T04:30:35.450Z",
    "body": (
        '<h2>The Blog</h2>'
        '<p>This is my blog!</p>'
    ),
})
root_page.add_child(instance=blog_page)

news_page = NewsPage(**{
    "title": "News Page",
    "slug": "news-page",
    "live": True,
    "has_unpublished_changes": False,
    "url_path": "/news/",
    "owner": admin,
    "first_published_at": "2018-08-28T04:30:35.450Z",
    "last_published_at": "2018-08-28T04:30:35.450Z",
    "body": (
        '<h2>The News</h2>'
        '<p>This is some news!</p>'
    ),
})
root_page.add_child(instance=news_page)


site = Site.objects.create(
    **{
        "hostname": "localhost",
        "port": 80,
        "site_name": "Checklist Demo Site",
        "root_page": root_page,
        "is_default_site": True
    }
)
