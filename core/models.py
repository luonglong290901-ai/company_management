from django.db import models

# Create your models here.
class Company(models.Model):
    company_name = models.CharField(max_length=255)
    english_name = models.CharField(max_length=255, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=50, blank=True)
    tax_code = models.CharField(max_length=50, blank=True)
    website = models.CharField(max_length=255, blank=True)
    operation_date = models.DateField(null=True, blank=True)
    legal_representative = models.CharField(max_length=505, blank=True)
    industry = models.TextField(blank=True)
    main_customer = models.TextField(blank=True)
    branches_in_vn = models.TextField(blank=True)
    owner = models.TextField(blank=True)
    capital = models.CharField(max_length=255, null=True, blank=True)
    revenue = models.CharField(max_length=255, blank=True)
    export_info = models.TextField(blank=True)
    scale = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True, help_text="Ghi chú về công ty")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

class Contact(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contacts')

    contact_name = models.CharField(max_length=100)
    position = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank = True)
    email = models.CharField(max_length=100, blank = True)
    department = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contact_name} ({self.company.company_name})"


class LicenseRecord(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='license_records')

    product_name = models.CharField(max_length=255)
    product_id = models.CharField(max_length=20)
    quantity = models.IntegerField()
    product_seats = models.IntegerField()
    license_type = models.CharField(max_length=100)
    start_date = models.DateField()
    expiration_date = models.DateField()
    partner = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name} - {self.company.company_name}"


class InfringementOverview(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='infringement_overviews')

    number_of_infringement_computers = models.IntegerField()
    infringement_time = models.CharField(max_length=255)
    event_to_quotes = models.TextField()
    infringement_softwares = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True)
    infringement_address = models.TextField(blank=True)
    other_softwares = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Infringement - {self.company.company_name} - {self.infringement_time}"

