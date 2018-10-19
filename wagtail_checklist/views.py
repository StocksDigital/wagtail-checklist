import logging

from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ChecklistSerializer

logger = logging.getLogger(__name__)


class WagtailLoginRequiredMixin(UserPassesTestMixin):
    """
    Denies users access if they do not have permission to log into the Wagtail admin.
    Redirects failing users to the Wagtail admin login screen.
    """
    login_url = 'wagtailadmin_login'
    raise_exception = False

    def test_func(self):
        if not self.request.user:
            return False

        user_permissions = self.request.user.get_all_permissions()
        return 'wagtailadmin.access_admin' in user_permissions


class WagtailLoginRequiredAPIMixin(WagtailLoginRequiredMixin):
    """
    Denies users access if they do not have permission to log into the Wagtail admin.
    Throws an exception if users fail the test.
    """
    login_url = None
    raise_exception = True


class ChecklistAPIEndpoint(WagtailLoginRequiredAPIMixin, APIView):
    """
    Receives Wagtail Page data from the admin edit / create page.
    Returns set of validation errors / warnings.
    """
    def post(self, request, *args, **kwargs):
        serializer = ChecklistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.create(serializer.validated_data)
        return Response(response_data, status=200)
