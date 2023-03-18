from django.urls import path
from api.views import (LandlordList, LandlordDetail, TenantList, TenantDetail, 
                        MaintenanceRequestList, MaintenanceRequestDetail,
                        PropertyList, PropertyDetail, LeaseList, 
                        LeaseDetail, PaymentDetail, PaymentList,)
                        
urlpatterns = [
    path('landlords/', LandlordList.as_view(), name='landlord-list'),
    path('landlords/<int:pk>', LandlordDetail.as_view(), name='landlord-detail'),

    path('property/', PropertyList.as_view(), name='property-list'),
    path('property/<int:pk>', PropertyDetail.as_view(), name='property-detail'),

    path('tenant/', TenantList.as_view(), name='tenant-list'),
    path('tenant/<int:pk>', TenantDetail.as_view(), name='tenant-detail'),

    path('lease/', LeaseList.as_view(), name='lease-list'),
    path('lease/<int:pk>', LeaseDetail.as_view(), name='lease-detail'),

    path('payment/', PaymentList.as_view(), name='payment-list'),
    path('payment/<int:pk>', PaymentDetail.as_view(), name='payment-detail'),

    path('maintenance/', MaintenanceRequestList.as_view(), name='maintenance-list'),
    path('maintenance/<int:pk>', MaintenanceRequestDetail.as_view(), name='maintenance-detail'),
]