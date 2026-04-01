from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from .models import CustomUser, UserChangeLog
from .permissions import IsAdminOrOwner
from .serializers import CustomUserSerializer, UserDetailSerializer, AdminUserSerializer
from fundraisers.models import Fundraiser

class CustomUserList(APIView):
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAdminUser()]   # the list can view only admin
        return super().get_permissions()         # for POST take AllowAny


    def get(self, request):
        deleted_param = request.query_params.get("deleted", "").lower()
        wants_deleted = deleted_param in ("1", "true", "yes")

        if wants_deleted:
            users = CustomUser.objects.filter(is_active=False)
        else:
            users = CustomUser.objects.filter(is_active=True)
        #users = CustomUser.objects.filter(is_active=True)
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

    def get_serializer_class(self, request):
        if request.user.is_staff:
            return AdminUserSerializer
        return UserDetailSerializer

 
    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        self.check_object_permissions(request, user)

        serializer_class = self.get_serializer_class(request)
        serializer = serializer_class(user, context={"request": request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        self.check_object_permissions(request, user)
        serializer_class = self.get_serializer_class(request)
        
        editable_fields = ["username", "first_name", "last_name", "email"]
        if request.user.is_staff:
            editable_fields.extend(["is_active", "is_staff"])

        old_values = {
            field: getattr(user, field)
            for field in editable_fields
        }

        serializer = serializer_class(
            instance=user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            updated_user = serializer.save()

            change_logs_to_create = []

            for field in editable_fields:
                old_value = old_values[field]
                new_value = getattr(updated_user, field)

                if old_value != new_value:
                    change_logs_to_create.append(
                        UserChangeLog(
                            user=updated_user,
                            changed_by=request.user,
                            field_name=field,
                            old_value="" if old_value is None else str(old_value),
                            new_value="" if new_value is None else str(new_value),
                        )
                    )

            if change_logs_to_create:
                UserChangeLog.objects.bulk_create(change_logs_to_create)

            response_serializer = serializer_class(updated_user, context={"request": request})
            return Response(response_serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        self.check_object_permissions(request, user)

        old_is_active = user.is_active
        user.is_active = False
        user.save(update_fields=["is_active"])

        # Логирование удаления (деактивации) пользователя
        UserChangeLog.objects.create(
            user=user,
            changed_by=request.user,
            field_name="is_active",
            old_value=str(old_is_active),
            new_value="False"
        )

        Fundraiser.objects.filter(owner=user, is_deleted=False).update(
            is_deleted=True,
            is_open=False
        )

        return Response(
            {"message": "User successfully deleted"},
            status=status.HTTP_200_OK
        )


class DeletedUserDetail(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk, is_active=False)
        self.check_object_permissions(request, user)

        serializer_class = AdminUserSerializer if request.user.is_staff else UserDetailSerializer
        serializer = serializer_class(user, context={"request": request})
        return Response(serializer.data)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user_id": user.id,
            "email": user.email,
            "is_staff": user.is_staff,
        })


class RestoreUser(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk, is_active=False)
        user.is_active = True
        user.save(update_fields=["is_active"])

        Fundraiser.objects.filter(owner=user, is_deleted=True).update(
            is_deleted=False,
            is_open=True
        )
        
        return Response(
            {"message": "User and related fundraisers restored successfully"},
            status=status.HTTP_200_OK
        )