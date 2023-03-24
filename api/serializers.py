from rest_framework import serializers
from .models import Landlord, Property, Tenant, Lease, Payment, MaintenanceRequest


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRequest
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class LeaseSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Lease
        fields = '__all__'


class TenantSerializer(serializers.ModelSerializer):
    leases = LeaseSerializer(many=True, read_only=True)
    maintenance_requests = MaintenanceRequestSerializer(
        many=True, read_only=True)

    class Meta:
        model = Tenant
        fields = '__all__'


class PropertySerializer(serializers.ModelSerializer):
    tenants = TenantSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = '__all__'


class LandlordSerializer(serializers.ModelSerializer):
    properties = PropertySerializer(many=True, read_only=True)

    class Meta:
        model = Landlord
        fields = '__all__'
