from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate,
)
from accounts.api.serializers import (
    UserSerializer,
    SignupSerializer,
    LoginSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]


class AccountViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        """
        Sign up using username, email and password
        """
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check the input',
                'errors': serializer.errors,
            }, status=400)

        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        })

    @action(methods=['POST'], detail=False)
    def login(self, request):
        """
        Get username and password from request
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check the input',
                'errors': serializer.errors,
            }, status=400)
        # if validated, continue with login
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        if not User.objects.filter(username=username).exists():
            return Response({
                'success': False,
                'message': 'User does not exist',
            }, status=400)

        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                'success': False,
                'message': 'Username and password do not match'
            }, status=400)

        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        })

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        """
        Check user login status
        """
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        """
        User log out
        """
        django_logout(request)
        return Response({'success': True})
