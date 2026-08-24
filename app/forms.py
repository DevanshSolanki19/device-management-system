from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import (
    Bank,
    DeviceDetails,
    OfficeDetails,
    PaymentMode,
    Role,
    StateOffice,
    StockEntry,
    Vendor,
)


ROLE_CHOICES = [
    ("Admin", "Admin"),
    ("Stock Manager(H.O.)", "Stock Manager(H.O.)"),
    ("Executive(H.O.)", "Executive(H.O.)"),
    ("SPM (State Office)", "SPM (State Office)"),
    ("Executive(State Office)", "Executive(State Office)"),
]


class LoginForm(forms.Form):
    Role = forms.ChoiceField(choices=ROLE_CHOICES)
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class SignupForm(LoginForm):
    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError("This username already exists.")
        return username

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ["v_name", "address", "city", "state", "pin", "mobile", "gstin"]

    def clean_gstin(self):
        return self.cleaned_data["gstin"].strip().upper()


class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ["name"]


class StateOfficeForm(forms.ModelForm):
    class Meta:
        model = StateOffice
        fields = ["state", "state_iso_code"]

    def clean_state_iso_code(self):
        return self.cleaned_data["state_iso_code"].strip().upper()


class DeviceDetailsForm(forms.ModelForm):
    class Meta:
        model = DeviceDetails
        fields = ["device_name"]


class PaymentModeForm(forms.ModelForm):
    class Meta:
        model = PaymentMode
        fields = ["mode"]


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ["role"]


class OfficeDetailsForm(forms.ModelForm):
    class Meta:
        model = OfficeDetails
        fields = [
            "name",
            "state",
            "division",
            "district",
            "city",
            "address",
            "pin",
            "phone_no",
            "mobile_no",
        ]


class StockEntryForm(forms.ModelForm):
    class Meta:
        model = StockEntry
        fields = [
            "purchase_order_number",
            "device_type",
            "device_received_date",
            "device_number",
        ]


class ManagedUserForm(forms.Form):
    login_id = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    office_id = forms.IntegerField()
    role = forms.CharField(max_length=100)
    login_status = forms.BooleanField(required=False)
    create_at = forms.DateField(required=False)
    updated_at = forms.DateField(required=False)
    token = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, user=None, creating=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["password"].required = creating

    def clean_login_id(self):
        login_id = self.cleaned_data["login_id"].strip()
        users = get_user_model().objects.filter(username=login_id)
        if self.user:
            users = users.exclude(pk=self.user.pk)
        if users.exists():
            raise forms.ValidationError("This login ID already exists.")
        return login_id

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password, user=self.user)
        return password

    def clean_office_id(self):
        office_id = self.cleaned_data["office_id"]
        if not OfficeDetails.objects.filter(pk=office_id).exists():
            raise forms.ValidationError("Office ID does not exist.")
        return office_id
