from rest_framework import serializers
from .models import Fundraiser, Pledge
 
class FundraiserSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    ####
    amount_raised = serializers.SerializerMethodField()
    
    def get_amount_raised(self, obj):
        """Count raised sum"""
        return sum([pledge.amount for pledge in obj.pledges.all()])
###
    class Meta:
        model = Fundraiser
        fields = '__all__'

class PledgeSerializer(serializers.ModelSerializer):
    supporter = serializers.ReadOnlyField(source='supporter.id')
    fundraiser = serializers.PrimaryKeyRelatedField(
        queryset=Fundraiser.objects.filter(is_deleted=False))  # added filter for deleted
        
    class Meta:
        model = Pledge
        fields = "__all__"

    def validate(self, data):
        """Check if the pledge exceeds the amount of the fundraiser"""
        fundraiser = data.get('fundraiser')
        amount = data.get('amount')
        
        if fundraiser and amount:
            # Count total pledges
            total_pledges = sum([
                pledge.amount for pledge in fundraiser.pledges.all()
            ])
            
            # If new pledge exceeds the rest of the amount 
            if total_pledges + amount > fundraiser.goal:
                raise serializers.ValidationError(
                    f"Cannot pledge more than goal. "
                    f"Goal: {fundraiser.goal}, "
                    f"Already raised: {total_pledges}, "
                    f"Remaining: {fundraiser.goal - total_pledges}"
                )
        
        return data

class FundraiserDetailSerializer(FundraiserSerializer):
    pledges = PledgeSerializer(many=True, read_only=True)
    amount_raised = serializers.SerializerMethodField()
    goal = serializers.ReadOnlyField() # ← not allowed to update
    description = serializers.ReadOnlyField()  # ← not allowed to update

    def get_amount_raised(self, obj):
        """Count raised sum"""
        return sum([pledge.amount for pledge in obj.pledges.all()])

    def update(self, instance, validated_data):
        forbidden_fields = ["title", "description"]

        for field in forbidden_fields:
            if field in validated_data:
                raise serializers.ValidationError(
                    {"Title and description fields cannot be modified."}
                )
        # instance.title = validated_data.get('title', instance.title)
        # instance.description = validated_data.get('description', instance.description)
        # not allowed to update
        instance.goal = validated_data.get('goal', instance.goal)
        instance.image = validated_data.get('image', instance.image)
        instance.is_open = validated_data.get('is_open', instance.is_open)
        instance.date_created = validated_data.get('date_created', instance.date_created)
        instance.owner = validated_data.get('owner', instance.owner)
        instance.save()
        return instance

class PledgeDetailSerializer(PledgeSerializer):
    pledges = PledgeSerializer(many=True, read_only=True)
    amount = serializers.ReadOnlyField()  # ← amount not allowed to update

    def update(self, instance, validated_data):
        instance.supporter = validated_data.get('supporter', instance.supporter)
        instance.fundraiser = validated_data.get('fundraiser', instance.fundraiser)
        # amount not allowed to update - read-only
        instance.comment = validated_data.get('comment', instance.comment)
        instance.anonymous = validated_data.get('anonymous', instance.anonymous)
        instance.save()
        return instance