from django.conf import settings
from django.db import models
from django.utils import timezone


class Role(models.Model):
    role = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["role"]

    def __str__(self):
        return self.role


class StateOffice(models.Model):
    state = models.CharField(max_length=100, unique=True)
    state_iso_code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ["state"]

    @property
    def state_id(self):
        """Compatibility property used by the original template."""
        return self.pk

    def __str__(self):
        return self.state


class OfficeDetails(models.Model):
    name = models.CharField(max_length=150)
    state = models.ForeignKey(
        StateOffice, on_delete=models.PROTECT, related_name="offices"
    )
    division = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    pin = models.CharField(max_length=10)
    phone_no = models.CharField(max_length=20)
    mobile_no = models.CharField(max_length=20)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "state", "city"], name="unique_office_in_city"
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.city}"


class Vendor(models.Model):
    v_name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin = models.CharField(max_length=10)
    mobile = models.CharField(max_length=20)
    gstin = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ["v_name"]

    def __str__(self):
        return self.v_name


class Bank(models.Model):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PaymentMode(models.Model):
    mode = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["mode"]

    def __str__(self):
        return self.mode


class DeviceDetails(models.Model):
    device_name = models.CharField(max_length=150, unique=True)

    class Meta:
        ordering = ["device_name"]

    def __str__(self):
        return self.device_name


class StockEntry(models.Model):
    purchase_order_number = models.CharField(max_length=50)
    device_type = models.ForeignKey(
        DeviceDetails, on_delete=models.PROTECT, related_name="stock_entries"
    )
    device_received_date = models.DateField()
    device_number = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["-device_received_date", "device_number"]

    def __str__(self):
        return f"{self.device_number} - {self.device_type}"


class DMSUserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dms_profile"
    )
    office = models.ForeignKey(
        OfficeDetails,
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )
    login_status = models.BooleanField(default=True)
    create_at = models.DateField(default=timezone.localdate)
    updated_at = models.DateField(default=timezone.localdate)
    token = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return self.user.username
