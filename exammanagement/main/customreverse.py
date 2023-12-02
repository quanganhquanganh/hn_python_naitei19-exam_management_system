from django.conf import settings
from django.urls import reverse
from django.utils.functional import lazy


def customreverse(viewname, urlconf=None, args=None, kwargs=None, current_app=None):
    url = reverse(
        viewname, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app
    )
    if settings.FORCE_SCRIPT_NAME:
        url = url.replace(settings.FORCE_SCRIPT_NAME, "/")
    return url

customreverse_lazy = lazy(customreverse, str)
