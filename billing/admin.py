from django.contrib import admin
from .models import Claim, Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'specialty', 'npi_number', 'is_active')
    search_fields = ('first_name', 'last_name', 'npi_number')
    list_filter = ('provider_type', 'is_active')


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_id', 'patient_name', 'payer', 'status', 'charge_amount')
    list_filter = ('status',)
    search_fields = ('claim_id', 'patient_name')