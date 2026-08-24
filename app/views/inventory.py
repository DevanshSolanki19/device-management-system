from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from ..forms import StockEntryForm
from ..models import DeviceDetails as DeviceDetailsModel
from ..models import StockEntry
from .common import form_error


def _stock_rows():
    return StockEntry.objects.values_list(
        "id",
        "purchase_order_number",
        "device_type__device_name",
        "device_received_date",
        "device_number",
    )


def _stock_form_data(post_data):
    device = DeviceDetailsModel.objects.filter(
        device_name=post_data.get("Device_type")
    ).first()
    return {
        "purchase_order_number": post_data.get("purchase_order_number"),
        "device_type": device.pk if device else None,
        "device_received_date": post_data.get("Device_received_date"),
        "device_number": post_data.get("Device_number"),
    }


@login_required
@require_GET
def stock_entry_details(request):
    context = {
        "data1": DeviceDetailsModel.objects.values_list("device_name"),
        "data": _stock_rows(),
    }
    return render(request, "Stock_Entry.html", context)


@login_required
@require_POST
def stock_entry_info(request):
    form = StockEntryForm(_stock_form_data(request.POST))
    if form.is_valid():
        form.save()
        return redirect("stock_entry_details")
    return render(
        request,
        "Stock_Entry.html",
        {
            "data1": DeviceDetailsModel.objects.values_list("device_name"),
            "data": _stock_rows(),
            "error": form_error(form),
        },
    )


@login_required
@require_GET
def stock_entry_Edit(request, id):
    item = get_object_or_404(StockEntry.objects.select_related("device_type"), pk=id)
    data = (
        item.pk,
        item.purchase_order_number,
        item.device_type.device_name,
        item.device_received_date.isoformat(),
        item.device_number,
    )
    return render(
        request,
        "Stock_Entry_update.html",
        {"data": data, "data1": DeviceDetailsModel.objects.values_list("device_name")},
    )


@login_required
@require_POST
def stock_entry_update(request):
    item = get_object_or_404(StockEntry, pk=request.POST.get("id"))
    form = StockEntryForm(_stock_form_data(request.POST), instance=item)
    if form.is_valid():
        form.save()
        return redirect("stock_entry_details")
    return redirect("stock_entry_Edit", id=item.pk)


@login_required
@require_POST
def stock_entry_delete(request, id):
    get_object_or_404(StockEntry, pk=id).delete()
    return redirect("stock_entry_details")


@login_required
@require_http_methods(["GET", "POST"])
def Device(request):
    stock = StockEntry.objects.select_related("device_type")
    if request.method == "POST":
        device_type = request.POST.get("Device_type")
        quantity_text = request.POST.get("device_quantity", "")
        if device_type:
            stock = stock.filter(device_type__device_name=device_type)
        if quantity_text.isdigit() and int(quantity_text) > 0:
            stock = stock[: int(quantity_text)]

    data = [(item.pk, item.device_number, item.device_type.device_name) for item in stock]
    context = {
        "data1": DeviceDetailsModel.objects.values_list("device_name"),
        "data": data,
    }
    return render(request, "Device.html", context)
