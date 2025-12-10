from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from .models import Usuario
from .serializers import UsuarioSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_login(request):
    """
    Login con usuario y contraseña
    Body: {"username": "user", "password": "pass"}
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'username y password son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Credenciales inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'Usuario inactivo'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    login(request, user)
    serializer = UsuarioSerializer(user)
    
    return Response({
        'success': True,
        'message': 'Login exitoso',
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth_logout(request):
    """
    Logout de la sesión actual
    """
    logout(request)
    return Response({
        'success': True,
        'message': 'Logout exitoso'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_me(request):
    """
    Obtener información del usuario logueado
    Si no hay sesión válida, retorna success: false
    """
    if request.user and request.user.is_authenticated:
        serializer = UsuarioSerializer(request.user)
        return Response({
            'success': True,
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': 'No hay sesión válida'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_register(request):
    """
    Registrar nuevo usuario
    Body: {
        "username": "user",
        "password": "pass",
        "first_name": "Juan",
        "apellido_paterno": "Pérez",
        "apellido_materno": "García",
        "correo_electronico": "juan@example.com",
        "codigo_tipo_usuario": 1,
        "codigo_nivel_acceso": 3,
        "codigo_sucursal": 1
    }
    """
    serializer = UsuarioSerializer(data=request.data)
    
    if serializer.is_valid():
        usuario = serializer.save()
        
        # Login automático después del registro
        login(request, usuario)
        
        return Response({
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'user': UsuarioSerializer(usuario).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
