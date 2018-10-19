from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.static import static

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.core import urls as wagtail_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^cms/', include(wagtailadmin_urls)),
 	path(r'wagtail_checklist/', include('wagtail_checklist.urls')),
    re_path(r'', include(wagtail_urls)),
]
