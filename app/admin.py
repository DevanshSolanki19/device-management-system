from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import (
    Bank,
    DMSUserProfile,
    DeviceDetails,
    OfficeDetails,
    PaymentMode,
    Role,
    StateOffice,
    StockEntry,
    Vendor,
)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("v_name", "city", "state", "mobile", "gstin")
    search_fields = ("v_name", "city", "gstin")


@admin.register(StateOffice)
class StateOfficeAdmin(admin.ModelAdmin):
    list_display = ("state", "state_iso_code")
    search_fields = ("state", "state_iso_code")


@admin.register(OfficeDetails)
class OfficeDetailsAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "division", "district", "city")
    list_filter = ("state",)
    search_fields = ("name", "district", "city")


@admin.register(StockEntry)
class StockEntryAdmin(admin.ModelAdmin):
    list_display = (
        "device_number",
        "device_type",
        "purchase_order_number",
        "device_received_date",
    )
    list_filter = ("device_type", "device_received_date")
    search_fields = ("device_number", "purchase_order_number")


@admin.register(Bank, PaymentMode, Role, DeviceDetails)
class SmallMasterAdmin(admin.ModelAdmin):
    search_fields = ("id",)


class DMSUserProfileInline(admin.StackedInline):
    model = DMSUserProfile
    can_delete = False
    extra = 0


User = get_user_model()
admin.site.unregister(User)


@admin.register(User)
class DMSUserAdmin(UserAdmin):
    inlines = [DMSUserProfileInline]
