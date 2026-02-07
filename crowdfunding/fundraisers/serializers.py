from rest_framework import serializers
from .models import Fundraiser, Pledge
 
class FundraiserSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    class Meta:
        model = Fundraiser
        fields = '__all__'

class PledgeSerializer(serializers.ModelSerializer):
    supporter = serializers.ReadOnlyField(source='supporter.id')
    fundraiser = serializers.PrimaryKeyRelatedField(queryset=Fundraiser.objects.filter(is_deleted=False))  # added filter for deleted

    class Meta:
        model = Pledge
        fields = "__all__"

class FundraiserDetailSerializer(FundraiserSerializer):
    pledges = PledgeSerializer(many=True, read_only=True)
    goal = serializers.ReadOnlyField() # ← not allowed to update
    description = serializers.ReadOnlyField()  # ← not allowed to update

    def update(self, instance, validated_data):
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