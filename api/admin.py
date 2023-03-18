from django.contrib import admin
from api.models import Landlord, Tenant, Property, Payment, Lease, MaintenanceRequest
# Register your models here.
admin.site.register(Landlord)
admin.site.register(Tenant)
admin.site.register(Property)
admin.site.register(Payment)
admin.site.register(Lease)
admin.site.register(MaintenanceRequest)
