from rest_framework import serializers
from .models import Fundraiser, Pledge
 
class FundraiserSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    
    class Meta:
        model = Fundraiser
        fields = '__all__'

class PledgeSerializer(serializers.ModelSerializer):
    supporter = serializers.ReadOnlyField(source='supporter.id')
    
    class Meta:
        model = Pledge
        fields = "__all__"

class FundraiserDetailSerializer(FundraiserSerializer):
    pledges = PledgeSerializer(many=True, read_only=True)
