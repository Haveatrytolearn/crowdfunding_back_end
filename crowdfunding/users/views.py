from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from .models import CustomUser
from .permissions import IsAdminOrOwner
from .serializers import CustomUserSerializer, UserDetailSerializer

class CustomUserList(APIView):
    #permission_classes = [permissions.IsAdminUser]
#
    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]  # anyone can register
        return [permissions.IsAdminUser()]  # only admin can list users

#
    def get(self, request):
        users = CustomUser.objects.filter(is_active=True)
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

class CustomUserDetail(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrOwner
    ]
 
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        self.check_object_permissions(request, user)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        self.check_object_permissions(request, user)
        serializer = CustomUserSerializer(
            instance=user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    def delete(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        self.check_object_permissions(request, user)
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(
            {'message': 'User successfully deleted'},
            status=status.HTTP_200_OK
        )

class DeletedUserList(APIView):
    permission_classes = [permissions.IsAdminUser]  # Only admins can see deleted
    
    def get(self, request):
        user = CustomUser.objects.filter(is_active=False)
        serializer = UserDetailSerializer(user, many=True)
        return Response(serializer.data)

class DeletedUserDetail(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]  # Only admins and ownerscan see deleted
    
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk, is_active=False)
        self.check_object_permissions(request, user)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email
        })
