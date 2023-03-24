from django.db import models


class Landlord(models.Model):
    landlord_name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    phone = models.IntegerField()

    def __str__(self):
        return self.landlord_name + " " + self.email


class Property(models.Model):
    landlord = models.ForeignKey(
        Landlord, on_delete=models.CASCADE, related_name='properties')
    property_name = models.CharField(max_length=30)
    number_of_units = models.IntegerField()
    water_rate = models.IntegerField()
    electricity_rate = models.IntegerField(default=0)
    mpesa_paybill = models.CharField(max_length=30)
    address = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    zip = models.CharField(max_length=30)

    def __str__(self):
        return self.property_name


class Tenant(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='tenants')
    tenant_name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    phone = models.IntegerField()
    unit_name = models.CharField(max_length=30)
    balance = models.IntegerField()

    def __str__(self):
        return self.tenant_name


class Lease(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='leases')
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name='leases')
    deposit = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return str(self.id)


class Payment(models.Model):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name='payments')
    lease = models.ForeignKey(
        Lease, on_delete=models.CASCADE, related_name='payments')
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='payments')
    status = models.BooleanField(default=False)
    payment_date = models.DateTimeField()
    payment_amount = models.IntegerField()

    def __str__(self):
        return str(self.id) + " " + str(self.tenant)


class MaintenanceRequest(models.Model):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name='maintenance_requests')
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='maintenance_requests')
    request_date = models.DateTimeField()
    description = models.CharField(max_length=200)
    status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
