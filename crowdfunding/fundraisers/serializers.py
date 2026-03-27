from rest_framework import serializers
from .models import Fundraiser, Pledge
 
class FundraiserSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    amount_raised = serializers.SerializerMethodField()
    
    def get_amount_raised(self, obj):
        """Count raised sum"""
        return sum([pledge.amount for pledge in obj.pledges.all()])

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
        read_only_fields = ("is_deleted",)

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

class FundraiserDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    pledges = serializers.SerializerMethodField()
    amount_raised = serializers.SerializerMethodField()
    has_donated = serializers.SerializerMethodField()
    date_created = serializers.ReadOnlyField()

    class Meta:
        model = Fundraiser
        fields = [
            "id",
            "owner",
            "title",
            "description",
            "goal",
            "image",
            "is_open",
            "is_deleted",
            "date_created",
            "amount_raised",
            "pledges",
            "has_donated",
        ]

    def get_pledges(self, obj):
        qs = obj.pledges.filter(is_deleted=False)
        return PledgeSerializer(qs, many=True).data

    def get_amount_raised(self, obj):
        return sum([p.amount for p in obj.pledges.filter(is_deleted=False)])

    def get_has_donated(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return obj.pledges.filter(
            supporter=request.user,
            is_deleted=False
        ).exists()

    def update(self, instance, validated_data):
        forbidden_fields = ["owner", "date_created"]

        for field in forbidden_fields:
            if field in validated_data:
                raise serializers.ValidationError(
                    {"The owner and creation date fields cannot be modified."}
                )

        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.goal = validated_data.get("goal", instance.goal)
        instance.image = validated_data.get("image", instance.image)
        instance.is_open = validated_data.get("is_open", instance.is_open)
        instance.save()
        return instance

class PledgeDetailSerializer(PledgeSerializer):
    amount = serializers.ReadOnlyField()  # amount not allowed to update
    fundraiser = serializers.ReadOnlyField()
    supporter = serializers.ReadOnlyField(source='supporter.id')

    def update(self, instance, validated_data):

        # amount, supporter and fundraiser not allowed to update - read-only
        instance.comment = validated_data.get('comment', instance.comment)
        instance.anonymous = validated_data.get('anonymous', instance.anonymous)
        instance.save()
        return instance