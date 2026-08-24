from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from ..forms import (
    BankForm,
    DeviceDetailsForm,
    PaymentModeForm,
    RoleForm,
    StateOfficeForm,
    VendorForm,
)
from ..models import (
    Bank,
    DeviceDetails as DeviceDetailsModel,
    PaymentMode,
    Role,
    StateOffice as StateOfficeModel,
    Vendor,
)
from .common import form_error


def _vendor_values(vendor):
    return (
        vendor.pk,
        vendor.v_name,
        vendor.address,
        vendor.city,
        vendor.state,
        vendor.pin,
        vendor.mobile,
        vendor.gstin,
    )


@login_required
@require_GET
def vendor(request):
    return render(request, "vendor.html")


@login_required
@require_POST
def vendor_info(request):
    form = VendorForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("vendor")
    return render(request, "vendor.html", {"error": form_error(form)})


@login_required
@require_GET
def vendorinfo(request):
    data = Vendor.objects.values_list(
        "id", "v_name", "address", "city", "state", "pin", "mobile", "gstin"
    )
    return render(request, "vendor_details.html", {"data": data})


@login_required
@require_POST
def vendor_delete(request, id):
    get_object_or_404(Vendor, pk=id).delete()
    return redirect("vendorinfo")


@login_required
@require_GET
def vendor_Edit(request, id):
    item = get_object_or_404(Vendor, pk=id)
    return render(request, "vendor_update.html", {"data": _vendor_values(item)})


@login_required
@require_POST
def vendor_update(request):
    item = get_object_or_404(Vendor, pk=request.POST.get("vid"))
    form = VendorForm(request.POST, instance=item)
    if form.is_valid():
        form.save()
        return redirect("vendorinfo")
    return render(
        request,
        "vendor_update.html",
        {"data": _vendor_values(item), "error": form_error(form)},
    )


@login_required
@require_GET
def bank_details(request):
    return render(
        request, "bank_list.html", {"data": Bank.objects.values_list("id", "name")}
    )


@login_required
@require_POST
def Bank_info(request):
    form = BankForm(request.POST)
    if form.is_valid():
        form.save()
    else:
        messages.error(request, form_error(form))
    return redirect("Bank_Details")


@login_required
@require_GET
def categoryEdit(request, id):
    bank = get_object_or_404(Bank, pk=id)
    return render(request, "Edit.html", {"data": (bank.pk, bank.name)})


@login_required
@require_POST
def categoryupdate(request):
    bank = get_object_or_404(Bank, pk=request.POST.get("bid"))
    form = BankForm(request.POST, instance=bank)
    if form.is_valid():
        form.save()
        return redirect("Bank_Details")
    return render(
        request,
        "Edit.html",
        {"data": (bank.pk, bank.name), "error": form_error(form)},
    )


@login_required
@require_POST
def Delete(request, id):
    get_object_or_404(Bank, pk=id).delete()
    return redirect("Bank_Details")


@login_required
@require_GET
def Stateoffice(request):
    return render(request, "Stateoffice.html")


@login_required
@require_POST
def Stateofficeadd(request):
    form = StateOfficeForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("Stateoffice")
    return render(request, "Stateoffice.html", {"error": form_error(form)})


@login_required
@require_GET
def Stateofficeinfo(request):
    data = StateOfficeModel.objects.values_list("id", "state", "state_iso_code")
    return render(request, "Stateoffice_list.html", {"data": data})


@login_required
@require_POST
def Stateoffice_delete(request, id):
    state = get_object_or_404(StateOfficeModel, pk=id)
    try:
        state.delete()
    except ProtectedError:
        messages.error(request, "This state is used by an office and cannot be deleted.")
    return redirect("Stateofficeinfo")


@login_required
@require_GET
def Stateoffice_Edit(request, id):
    state = get_object_or_404(StateOfficeModel, pk=id)
    return render(
        request,
        "Stateoffice_update.html",
        {"data": (state.pk, state.state, state.state_iso_code)},
    )


@login_required
@require_POST
def Stateoffice_update(request):
    state = get_object_or_404(StateOfficeModel, pk=request.POST.get("state_id"))
    form = StateOfficeForm(request.POST, instance=state)
    if form.is_valid():
        form.save()
        return redirect("Stateofficeinfo")
    return render(
        request,
        "Stateoffice_update.html",
        {
            "data": (state.pk, state.state, state.state_iso_code),
            "error": form_error(form),
        },
    )


@login_required
@require_GET
def Device_details(request):
    data = DeviceDetailsModel.objects.values_list("id", "device_name")
    return render(request, "device_details.html", {"data": data})


@login_required
@require_POST
def Device_info(request):
    form = DeviceDetailsForm(request.POST)
    if form.is_valid():
        form.save()
    else:
        messages.error(request, form_error(form))
    return redirect("Device_details")


@login_required
@require_GET
def Device_Edit(request, id):
    device = get_object_or_404(DeviceDetailsModel, pk=id)
    return render(request, "device_edit.html", {"data": (device.pk, device.device_name)})


@login_required
@require_POST
def Device_update(request):
    device = get_object_or_404(DeviceDetailsModel, pk=request.POST.get("id"))
    form = DeviceDetailsForm(request.POST, instance=device)
    if form.is_valid():
        form.save()
        return redirect("Device_details")
    return render(
        request,
        "device_edit.html",
        {"data": (device.pk, device.device_name), "error": form_error(form)},
    )


@login_required
@require_POST
def Device_delete(request, id):
    device = get_object_or_404(DeviceDetailsModel, pk=id)
    try:
        device.delete()
    except ProtectedError:
        messages.error(request, "This device type is used in stock and cannot be deleted.")
    return redirect("Device_details")


@login_required
@require_GET
def pay_mode(request):
    return render(
        request,
        "pay_mode.html",
        {"data": PaymentMode.objects.values_list("id", "mode")},
    )


@login_required
@require_POST
def pay_mode_info(request):
    form = PaymentModeForm(request.POST)
    if form.is_valid():
        form.save()
    else:
        messages.error(request, form_error(form))
    return redirect("pay_mode")


@login_required
@require_GET
def pay_mode_Edit(request, id):
    item = get_object_or_404(PaymentMode, pk=id)
    return render(request, "pay_mode_update.html", {"data": (item.pk, item.mode)})


@login_required
@require_POST
def pay_mode_update(request):
    item = get_object_or_404(PaymentMode, pk=request.POST.get("id"))
    form = PaymentModeForm(request.POST, instance=item)
    if form.is_valid():
        form.save()
        return redirect("pay_mode")
    return render(
        request,
        "pay_mode_update.html",
        {"data": (item.pk, item.mode), "error": form_error(form)},
    )


@login_required
@require_POST
def pay_mode_delete(request, id):
    get_object_or_404(PaymentMode, pk=id).delete()
    return redirect("pay_mode")


@login_required
@require_GET
def role_details(request):
    return render(
        request, "role.html", {"data": Role.objects.values_list("id", "role")}
    )


@login_required
@require_POST
def role_info(request):
    form = RoleForm(request.POST)
    if form.is_valid():
        role = form.save()
        Group.objects.get_or_create(name=role.role)
    else:
        messages.error(request, form_error(form))
    return redirect("role_details")


@login_required
@require_GET
def role_Edit(request, id):
    item = get_object_or_404(Role, pk=id)
    return render(request, "role_update.html", {"data": (item.pk, item.role)})


@login_required
@require_POST
def role_update(request):
    item = get_object_or_404(Role, pk=request.POST.get("id"))
    old_name = item.role
    form = RoleForm(request.POST, instance=item)
    if form.is_valid():
        role = form.save()
        group = Group.objects.filter(name=old_name).first()
        if group:
            group.name = role.role
            group.save(update_fields=["name"])
        else:
            Group.objects.get_or_create(name=role.role)
        return redirect("role_details")
    return render(
        request,
        "role_update.html",
        {"data": (item.pk, item.role), "error": form_error(form)},
    )


@login_required
@require_POST
def role_delete(request, id):
    item = get_object_or_404(Role, pk=id)
    role_name = item.role
    try:
        item.delete()
        Group.objects.filter(name=role_name).delete()
    except ProtectedError:
        messages.error(request, "This role is assigned to a user and cannot be deleted.")
    return redirect("role_details")
