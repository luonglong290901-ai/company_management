from django.contrib import admin
from .models import Company, Contact, LicenseRecord

# Register your models here.

#admin.site.register(Company)
#admin.site.register(Contact)

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1


class LicenseRecordInline(admin.TabularInline):
    model = LicenseRecord
    extra = 1

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'phone', 'industry')
    inlines = [ContactInline, LicenseRecordInline]

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('contact_name', 'company', 'phone')


@admin.register(LicenseRecord)
class LicenseRecordAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_id', 'company', 'license_type', 'expiration_date')
    