from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from ..forms import OfficeDetailsForm
from ..models import OfficeDetails as OfficeDetailsModel
from ..models import StateOffice as StateOfficeModel
from .common import form_error


def _office_form_data(post_data):
    return {
        "name": post_data.get("name"),
        "state": post_data.get("state_id"),
        "division": post_data.get("division"),
        "district": post_data.get("district"),
        "city": post_data.get("city"),
        "address": post_data.get("address"),
        "pin": post_data.get("pin"),
        "phone_no": post_data.get("phone_no"),
        "mobile_no": post_data.get("mobile_no"),
    }


def _office_values(item):
    return (
        item.pk,
        item.name,
        item.state_id,
        item.division,
        item.district,
        item.city,
        item.address,
        item.pin,
        item.phone_no,
        item.mobile_no,
    )


@login_required
@require_GET
def office_details(request):
    return render(request, "Office_details.html")


@login_required
@require_POST
def office_details_info(request):
    form = OfficeDetailsForm(_office_form_data(request.POST))
    if form.is_valid():
        form.save()
        return redirect("office_details")
    return render(request, "Office_details.html", {"error": form_error(form)})


@login_required
@require_GET
def office_details_list(request):
    data = OfficeDetailsModel.objects.values_list(
        "id",
        "name",
        "state_id",
        "division",
        "district",
        "city",
        "address",
        "pin",
        "phone_no",
        "mobile_no",
    )
    return render(request, "office_details_list.html", {"data": data})


@login_required
@require_POST
def office_details_delete(request, office_id):
    office = get_object_or_404(OfficeDetailsModel, pk=office_id)
    try:
        office.delete()
    except ProtectedError:
        messages.error(request, "This office is assigned to a user and cannot be deleted.")
    return redirect("office_details_list")


@login_required
@require_GET
def office_details_Edit(request, office_id):
    item = get_object_or_404(OfficeDetailsModel, pk=office_id)
    return render(request, "office_details_update.html", {"data": _office_values(item)})


@login_required
@require_POST
def office_details_update(request):
    item = get_object_or_404(OfficeDetailsModel, pk=request.POST.get("office_id"))
    form = OfficeDetailsForm(_office_form_data(request.POST), instance=item)
    if form.is_valid():
        form.save()
        return redirect("office_details_list")
    return render(
        request,
        "office_details_update.html",
        {"data": _office_values(item), "error": form_error(form)},
    )


@login_required
@require_GET
def issue_state_office(request):
    states = StateOfficeModel.objects.all()
    return render(request, "issue_state_office.html", {"states": states})


@login_required
@require_GET
def get_offices(request):
    state_id = request.GET.get("state_id")
    offices = OfficeDetailsModel.objects.none()
    if state_id and state_id.isdigit():
        offices = OfficeDetailsModel.objects.filter(state_id=state_id)
    data = [{"office_id": office.pk, "name": office.name} for office in offices]
    return JsonResponse(data, safe=False)
