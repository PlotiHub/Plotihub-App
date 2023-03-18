from rest_framework import serializers
from api.models import (Landlord, Property, MaintenanceRequest, 
                        Tenant, Lease, Payment)



class TenantSerializer(serializers.ModelSerializer):
    # property_detail = PropertySerializer(many=True, read_only=True)
    class Meta:
        model = Tenant
        fields = "__all__"  


class LandlordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Landlord
        fields = "__all__"
        # exclude = ('landlord',) 


class PropertySerializer(serializers.ModelSerializer):
    landlord = LandlordSerializer(many=True, read_only=True)
    tenants = TenantSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = "__all__" 


class LeaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lease
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Payment
        fields = "__all__"    


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRequest
        fields = "__all__"  
