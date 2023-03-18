from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework import mixins
from rest_framework import generics
from api.models import (Landlord, Property,Tenant, 
                        Lease, Payment, MaintenanceRequest)

from api.serializers import (LandlordSerializer, PropertySerializer,
                            TenantSerializer, LeaseSerializer,
                            PaymentSerializer, MaintenanceRequestSerializer)
# Create your views here.

# Using generic class-based views
class LandlordList(generics.ListCreateAPIView):
    queryset = Landlord.objects.all()
    serializer_class = LandlordSerializer

class LandlordDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Landlord.objects.all()
    serializer_class = LandlordSerializer

class PropertyList(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class PropertyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer


class TenantList(generics.ListCreateAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer


class TenantDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

class LeaseList(generics.ListCreateAPIView):
    queryset = Lease.objects.all()
    serializer_class = LeaseSerializer

class LeaseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lease.objects.all()
    serializer_class = LeaseSerializer

class PaymentList(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class PaymentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class MaintenanceRequestList(generics.ListCreateAPIView):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer

class MaintenanceRequestDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer