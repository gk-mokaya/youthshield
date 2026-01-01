from rest_framework import serializers
from donations.models import Donation
from programs.models import Program

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ['id', 'amount', 'currency', 'payment_method', 'status', 
                 'donor_name', 'donor_email', 'created_at']
        read_only_fields = ['created_at']

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ['id', 'title', 'description', 'category', 'image', 
                 'start_date', 'end_date', 'is_active']

