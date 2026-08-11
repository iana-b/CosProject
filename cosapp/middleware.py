import hashlib

from django.conf import settings

from .models import PageView

SKIP_PREFIXES = ('/static/', '/media/', '/admin/', '/__reload__/', '/__debug__/', '/stats/')


def hash_ip(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
    ip = ip or request.META.get('REMOTE_ADDR', '')
    return hashlib.sha256(f'{ip}{settings.SECRET_KEY}'.encode()).hexdigest()[:12]


class PageViewMiddleware:
    """Пишет просмотр страницы после ответа. Товар вьюха кладёт в request.viewed_product."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method == 'GET' and response.status_code == 200 and not request.path.startswith(SKIP_PREFIXES):
            PageView.objects.create(
                path=request.path[:200],
                product=getattr(request, 'viewed_product', None),
                user=request.user if request.user.is_authenticated else None,
                ip_hash=hash_ip(request),
            )
        return response
