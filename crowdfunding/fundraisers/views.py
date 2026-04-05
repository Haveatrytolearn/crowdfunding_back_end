from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Fundraiser, Pledge, FundraiserChangeLog
from .permissions import (
    IsOwnerOrReadOnly,
    IsSupporterOrReadOnly,
    IsAdminOrOwner,
    IsAdminFundraiserOwnerOrSupporter,
)
from .serializers import (
    FundraiserSerializer,
    PledgeSerializer,
    FundraiserDetailSerializer,
    PledgeDetailSerializer,
)

class FundraiserList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        
        deleted_param = request.query_params.get("deleted", "").lower()
        wants_deleted = deleted_param in ("1", "true", "yes")

        if wants_deleted:
            if not request.user.is_authenticated or not request.user.is_staff:
                raise PermissionDenied("Only admin users can view deleted fundraisers.")
            fundraisers = Fundraiser.objects.filter(is_deleted=True).order_by("id")
        else:
            fundraisers = Fundraiser.objects.filter(
                is_deleted=False,
                owner__is_active=True
            ).order_by("id")

        serializer = FundraiserSerializer(
            fundraisers,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = FundraiserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FundraiserDetail(APIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrOwner
    ]

    def get(self, request, pk):
        fundraiser = get_object_or_404(
            Fundraiser,
            pk=pk,
            is_deleted=False,
            owner__is_active=True
        )
        serializer = FundraiserDetailSerializer(
            fundraiser,
            context={"request": request}
        )
        return Response(serializer.data)

    def put(self, request, pk):
        fundraiser = get_object_or_404(
            Fundraiser,
            pk=pk,
            is_deleted=False,
            owner__is_active=True
        )
        self.check_object_permissions(request, fundraiser)

        editable_fields = ["title", "description", "goal", "image", "is_open"]

        old_values = {
            field: getattr(fundraiser, field)
            for field in editable_fields
        }

        serializer = FundraiserDetailSerializer(
            instance=fundraiser,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            updated_fundraiser = serializer.save()

            change_logs_to_create = []

            for field in editable_fields:
                if field in serializer.validated_data:
                    old_value = old_values[field]
                    new_value = getattr(updated_fundraiser, field)

                    if old_value != new_value:
                        change_logs_to_create.append(
                            FundraiserChangeLog(
                                fundraiser=updated_fundraiser,
                                changed_by=request.user,
                                field_name=field,
                                old_value="" if old_value is None else str(old_value),
                                new_value="" if new_value is None else str(new_value),
                            )
                        )

            if change_logs_to_create:
                FundraiserChangeLog.objects.bulk_create(change_logs_to_create)

            response_serializer = FundraiserDetailSerializer(
                updated_fundraiser,
                context={"request": request}
            )
            return Response(response_serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        fundraiser = get_object_or_404(
            Fundraiser,
            pk=pk,
            is_deleted=False,
            owner__is_active=True
        )
        self.check_object_permissions(request, fundraiser)

        fundraiser.is_deleted = True
        fundraiser.is_open = False
        fundraiser.save(update_fields=["is_deleted", "is_open"])

        fundraiser.pledges.filter(is_deleted=False).update(is_deleted=True)

        return Response(
            {"message": "Fundraiser successfully deleted"},
            status=status.HTTP_200_OK
        )


class DeletedFundraiserDetail(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    def get(self, request, pk):
        fundraiser = get_object_or_404(Fundraiser, pk=pk, is_deleted=True)
        self.check_object_permissions(request, fundraiser)

        serializer = FundraiserDetailSerializer(
            fundraiser,
            context={"request": request}
        )
        return Response(serializer.data)


class RestoreFundraiser(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    @transaction.atomic
    def post(self, request, pk):
        fundraiser = get_object_or_404(
            Fundraiser,
            pk=pk,
            is_deleted=True
        )

        if not fundraiser.owner.is_active:
            return Response(
                {
                    "detail": "The owner account must be restored before this fundraiser can be restored."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        self.check_object_permissions(request, fundraiser)

        fundraiser.is_deleted = False
        fundraiser.is_open = True
        fundraiser.save(update_fields=["is_deleted", "is_open"])

        fundraiser.pledges.filter(is_deleted=True).update(is_deleted=False)

        return Response(
            {"message": "Fundraiser and related pledges restored successfully"},
            status=status.HTTP_200_OK
        )


class PledgeList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        base_qs = Pledge.objects.filter(
            is_deleted=False,
            fundraiser__is_deleted=False
        )

        if request.user.is_staff:
            pledges = base_qs
        else:
            pledges = base_qs.filter(
                Q(supporter=request.user) |
                Q(fundraiser__owner=request.user)
            ).distinct()

        serializer = PledgeSerializer(pledges, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PledgeSerializer(data=request.data)
        if serializer.is_valid():
            spledge = serializer.save(supporter=request.user)
            total_raised = sum(
                p.amount for p in fundraiser.pledges.filter(is_deleted=False)
            )

            if total_raised >= fundraiser.goal and fundraiser.is_open:
                fundraiser.is_open = False
                fundraiser.save(update_fields=["is_open"])

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PledgesDetail(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminFundraiserOwnerOrSupporter
    ]

    def get(self, request, pk):
        pledge = get_object_or_404(
            Pledge,
            pk=pk,
            is_deleted=False,
            fundraiser__is_deleted=False
        )
        self.check_object_permissions(request, pledge)

        serializer = PledgeSerializer(pledge)
        return Response(serializer.data)

    def put(self, request, pk):
        pledge = get_object_or_404(
            Pledge,
            pk=pk,
            is_deleted=False,
            fundraiser__is_deleted=False
        )
        self.check_object_permissions(request, pledge)

        serializer = PledgeDetailSerializer(
            instance=pledge,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        pledge = get_object_or_404(
            Pledge,
            pk=pk,
            is_deleted=False,
            fundraiser__is_deleted=False
        )
        self.check_object_permissions(request, pledge)

        pledge.is_deleted = True
        pledge.save(update_fields=["is_deleted"])

        return Response(
            {"message": "Pledge successfully deleted"},
            status=status.HTTP_200_OK
        )