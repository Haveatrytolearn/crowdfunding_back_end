from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.db import transaction 

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Fundraiser, Pledge
from .permissions import IsOwnerOrReadOnly, IsSupporterOrReadOnly, IsAdminOrOwner
from .serializers import FundraiserSerializer, PledgeSerializer, FundraiserDetailSerializer, PledgeDetailSerializer

class FundraiserList(APIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        fundraisers = Fundraiser.objects.filter(
            is_deleted=False,
            owner__is_active=True)
        serializer = FundraiserSerializer(fundraisers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = FundraiserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
class FundraiserDetail(APIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrOwner
    ]
    
    def get(self, request, pk):
        fundraiser = get_object_or_404(Fundraiser, pk=pk, is_deleted=False, owner__is_active=True)
        serializer = FundraiserDetailSerializer(fundraiser)
        return Response(serializer.data)
 
 # Biagio version of the code   
    def put(self, request, pk):
        fundraiser = get_object_or_404(Fundraiser, pk=pk, is_deleted=False, owner__is_active=True)
        self.check_object_permissions(request, fundraiser)
        serializer = FundraiserDetailSerializer(
            instance=fundraiser,
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
        fundraiser = get_object_or_404(Fundraiser, pk=pk, is_deleted=False, owner__is_active=True)
        self.check_object_permissions(request, fundraiser)
        fundraiser.is_deleted = True
        fundraiser.is_open = False
        fundraiser.save(update_fields=["is_deleted", "is_open"])
        # soft delete pledges
        fundraiser.pledges.filter(is_deleted=False).update(is_deleted=True)
        return Response(
            {'message': 'Fundraiser successfully deleted'},
            status=status.HTTP_200_OK
        )
class DeletedFundraiserList(APIView):
    permission_classes = [permissions.IsAdminUser]  # Only admins can see deleted
    
    def get(self, request):
        fundraisers = Fundraiser.objects.filter(is_deleted=True)
        serializer = FundraiserDetailSerializer(fundraisers, many=True)
        return Response(serializer.data)

class DeletedFundraiserDetail(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]  # Only admins and owners can see deleted
    
    def get(self, request, pk):
        fundraiser = get_object_or_404(Fundraiser, pk=pk, is_deleted=True)
        self.check_object_permissions(request, fundraiser)
        serializer = FundraiserDetailSerializer(fundraiser)
        return Response(serializer.data)

    #def delete(self, request, pk):
        fundraiser = get_object_or_404(Fundraiser, pk=pk, is_deleted=True)
        self.check_object_permissions(request, fundraiser)
        fundraiser.is_deleted = True
        fundraiser.is_open = False
        fundraiser.save(update_fields=["is_deleted", "is_open"])
        return Response(
            {'message': 'Fundraiser successfully deleted'},
            status=status.HTTP_200_OK
        )


class RestoreFundraiser(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
    @transaction.atomic
    def post(self, request, pk):
        fundraiser = get_object_or_404(
            Fundraiser,
            pk=pk,
            is_deleted=True
        )

        # permission checks
        self.check_object_permissions(request, fundraiser)

        # Restore fundraiser
        fundraiser.is_deleted = False
        fundraiser.is_open = True
        fundraiser.save(update_fields=["is_deleted", "is_open"])

        # Restore related pledges
        fundraiser.pledges.filter(is_deleted=True).update(is_deleted=False)

        return Response(
            {"message": "Fundraiser and related pledges restored successfully"},
            status=status.HTTP_200_OK
        )


class PledgeList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        base_qs = Pledge.objects.filter(
            is_deleted=False,                 # NEW: hiding soft-deleted pledges
            fundraiser__is_deleted=False      # not to show pledges of the deleted fundraiser
        )

    # Admin can view all pledges
        if request.user.is_staff:
            pledges = base_qs
        else:
            pledges = base_qs.filter(
                Q(supporter=request.user) |  # His pledges
                Q(fundraiser__owner=request.user)  # Pledges to his fundraisers
            )
        
        serializer = PledgeSerializer(pledges, many=True)
        return Response(serializer.data)
    

    def post(self, request):
        serializer = PledgeSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save(supporter=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class PledgesDetail(APIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsSupporterOrReadOnly
    ]
    
    def get(self, request, pk):
        pledge = get_object_or_404(Pledge, pk=pk, is_deleted=False, fundraiser__is_deleted=False)
        serializer = PledgeSerializer(pledge)
        return Response(serializer.data)
    
 # Biagio version of the code   
    def put(self, request, pk):
        pledge = get_object_or_404(Pledge, pk=pk, is_deleted=False, fundraiser__is_deleted=False)
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