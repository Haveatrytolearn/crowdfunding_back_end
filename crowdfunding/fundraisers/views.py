from django.shortcuts import render, get_object_or_404

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
        fundraisers = Fundraiser.objects.filter(is_deleted=False)
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
        IsOwnerOrReadOnly
    ]
    
    def get(self, request, pk):
        fundraiser = get_object_or_404(Fundraiser, pk=pk, is_deleted=False)
        serializer = FundraiserDetailSerializer(fundraiser)
        return Response(serializer.data)
 
 # Biagio version of the code   
    def put(self, request, pk):
        fundraiser = get_object_or_404(Fundraiser, pk=pk, is_deleted=False)
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
        fundraiser = get_object_or_404(Fundraiser, pk=pk, is_deleted=False)
        self.check_object_permissions(request, fundraiser)
        fundraiser.is_deleted = True
        fundraiser.is_open = False
        fundraiser.save()
        return Response(
            {'message': 'Fundraiser successfully deleted'},
            status=status.HTTP_204_NO_CONTENT
        )
class DeletedFundraiserList(APIView):
    permission_classes = [permissions.IsAdminUser]  # Only admins can see deleted
    
    def get(self, request):
        fundraisers = Fundraiser.objects.filter(is_deleted=True)
        serializer = FundraiserDetailSerializer(fundraisers, many=True)
        return Response(serializer.data)

class DeletedFundraiserDetail(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]  # Only admins and ownerscan see deleted
    
    def get(self, request, pk):
        fundraiser = get_object_or_404(Fundraiser, pk=pk, is_deleted=True)
        self.check_object_permissions(request, fundraiser)
        serializer = FundraiserDetailSerializer(fundraiser)
        return Response(serializer.data)

class PledgeList(APIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly]


    def get(self, request):
        pledges = Pledge.objects.filter(fundraiser__is_deleted=False)
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
        pledge = get_object_or_404(Pledge, pk=pk)
        serializer = PledgeSerializer(pledge)
        return Response(serializer.data)
    
 # Biagio version of the code   
    def put(self, request, pk):
        pledge = get_object_or_404(Pledge, pk=pk)
        self.check_object_permissions(request, pledge)
        serializer = PledgeDetailSerializer(
            instance=pledge,
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
#

