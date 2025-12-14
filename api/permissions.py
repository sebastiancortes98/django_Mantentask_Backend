from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Permite acceso solo a usuarios con nivel de acceso Administrador (codigo_nivel_acceso=4)
    """
    message = "Solo administradores pueden acceder a este recurso."
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.codigo_nivel_acceso == 4
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Permite GET a cualquiera, pero POST/PUT/PATCH/DELETE solo a admins
    """
    message = "Solo administradores pueden modificar este recurso."
    
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return (
            request.user
            and request.user.is_authenticated
            and request.user.codigo_nivel_acceso == 4
        )


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Permite GET a cualquiera, POST/PUT/PATCH/DELETE solo a usuarios autenticados
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_authenticated
