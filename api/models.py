from django.db import models
# from django.contrib.auth.models import User


# Create your models here.
class Landlord(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    landlord_name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    phone = models.IntegerField() 
    # property = models.ForeignKey(Property, 
    #                             on_delete=models.CASCADE,
    #                             related_name="landlord")
    def __str__(self):
        return self.landlord_name + " " + self.email


class Property(models.Model):
    property_name = models.CharField(max_length=30)
    number_of_units = models.IntegerField()
    water_rate = models.IntegerField()
    electricity_rate = models.IntegerField(default=0)
    mpesa_paybill = models.CharField(max_length=30)
    address = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    zip = models.CharField(max_length=30)
    landlord = models.ForeignKey(Landlord, 
                                on_delete=models.CASCADE,
                                related_name="landlords")

    def __str__(self):
        return self.property_name




# Start of Tenant model
class Tenant(models.Model):
    tenant_name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    phone = models.IntegerField()
    property_id = models.ForeignKey(Property, 
                                on_delete=models.CASCADE,
                                related_name="tenants")
    unit_name = models.CharField(max_length=30)
    balance = models.IntegerField()


    def __str__(self):
        return self.tenant_name + " " + str(self.property_id)
# End of Tenant model

# Start of Lease model
class Lease(models.Model):
    property_id = models.ForeignKey(Property, 
                                on_delete=models.CASCADE,
                                related_name="lease")

    tenant_id = models.ForeignKey(Tenant, 
                                on_delete=models.CASCADE,
                                related_name="tenant")
    deposit = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return str(self.id)
# End of Lease model

# Start of Payment model
class Payment(models.Model):
    tenant_id = models.ForeignKey(Tenant, 
                                on_delete=models.CASCADE,
                                related_name="payment")

    lease_id = models.ForeignKey(Lease, 
                                on_delete=models.CASCADE,
                                related_name="payment")

    property_id = models.ForeignKey(Property, 
                                on_delete=models.CASCADE,
                                related_name="payment")
    status = models.BooleanField(default=False)
    payment_date = models.DateTimeField()
    payment_amount = models.IntegerField()

    def __str__(self):
        return str(self.id) + " " + str(self.tenant_id)
# End of Payment model

# Start of MaintenanceRequest model
class MaintenanceRequest(models.Model):
    tenant_id = models.ForeignKey(Tenant, 
                                on_delete=models.CASCADE,
                                related_name="maintenance")

    property_id = models.ForeignKey(Property, 
                                on_delete=models.CASCADE,
                                related_name="maintenance")

    request_date = models.DateTimeField()
    description = models.CharField(max_length=200)
    status = models.BooleanField(default=False)
# End of MaintenanceRequest model
