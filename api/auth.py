from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Usuario
from .serializers import UsuarioSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_login(request):
    """
    Login con usuario y contraseña
    Body: {"username": "user", "password": "pass"}
    Retorna: JWT access_token y refresh_token
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
    
    # Generar tokens JWT
    refresh = RefreshToken.for_user(user)
    serializer = UsuarioSerializer(user)
    
    return Response({
        'success': True,
        'message': 'Login exitoso',
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth_logout(request):
    """
    Logout - Con JWT solo necesita borrar el token en el frontend
    Este endpoint es opcional pero se mantiene para compatibilidad
    """
    return Response({
        'success': True,
        'message': 'Logout exitoso. Borra el token del localStorage.'
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
        
        # Con JWT: devolver tokens en el registro
        refresh = RefreshToken.for_user(usuario)
        
        return Response({
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': UsuarioSerializer(usuario).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
