from django.contrib import admin
from .models import Company, Contact, LicenseRecord, InfringementOverview, ImportedCSVFile, InfringementDetail

# Register your models here.

#admin.site.register(Company)
#admin.site.register(Contact)

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1


class LicenseRecordInline(admin.TabularInline):
    model = LicenseRecord
    extra = 1


class InfringementOverviewInline(admin.TabularInline):
    model = InfringementOverview
    extra = 1

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'phone', 'industry')
    inlines = [ContactInline, LicenseRecordInline, InfringementOverviewInline]

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('contact_name', 'company', 'phone')


@admin.register(LicenseRecord)
class LicenseRecordAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_id', 'company', 'license_type', 'expiration_date')


@admin.register(InfringementOverview)
class InfringementOverviewAdmin(admin.ModelAdmin):
    list_display = ('company', 'infringement_time', 'number_of_infringement_computers', 'infringement_softwares', 'event_to_quotes')


@admin.register(ImportedCSVFile)
class ImportedCSVFileAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'company', 'uploaded_by', 'uploaded_at')


@admin.register(InfringementDetail)
class InfringementDetailAdmin(admin.ModelAdmin):
    list_display = ('company', 'product', 'version', 'public_ip_address', 'active_mac')
    