from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import CsrfViewMiddleware


class DisableCSRFMiddleware(MiddlewareMixin):
    """
    Middleware para deshabilitar CSRF en endpoints de API
    Útil para desarrollo con REST Framework
    """
    def process_request(self, request):
        # Deshabilitar CSRF para todos los endpoints de /api/
        if request.path.startswith('/api/'):
            # Marcar como CSRF exento
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
