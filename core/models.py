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
    legal_representative = models.CharField(max_length=255, blank=True)
    industry = models.TextField(blank=True)
    main_customer = models.TextField(blank=True)
    branches_in_vn = models.TextField(blank=True)
    owner = models.CharField(max_length=500, blank=True)
    capital = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    revenue = models.CharField(max_length=255, blank=True)
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

