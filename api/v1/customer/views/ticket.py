# In your_app/serializers.py

from rest_framework import serializers

from apps.classified.models.ticket import *




class TicketMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = '__all__'

class SupportTicketSerializer(serializers.ModelSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = SupportTicket
        # FIX: Add 'order_id' to the list of fields
        fields = ('id', 'user', 'title', 'subject', 'priority', 'description',  'messages', 'order','status','slug')
        # Make the 'user' field read-only, as it's set automatically in the view
        read_only_fields = ('user',)



class ServiceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceReview
        # FIX: Add 'provider' and 'user' to the fields list, but make them read-only.
        fields = ('id', 'provider', 'user', 'rating', 'name', 'email', 'comment', 'created_at')
        read_only_fields = ('id', 'provider', 'user', 'created_at')

    def create(self, validated_data):
        # The `provider` and `user` objects are automatically passed into validated_data
        # by the serializer.save(provider=provider, user=user) call in the view.
        return ServiceReview.objects.create(**validated_data)

class ReportSerializer(serializers.ModelSerializer):

    # Match the keys from report_list_model.dart


    class Meta:
        model = Report
        fields = (
            'id', 'order_slug','slug',
             'status', 'report', 'created_at', 'updated_at'
        )

class ReportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportMessage
        fields = '__all__'