from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'api/$', views.ChecklistAPIEndpoint.as_view(), name='wagtail_checklist_api'),
]
