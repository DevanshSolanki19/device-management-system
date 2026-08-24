from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from ..forms import ManagedUserForm
from ..models import DMSUserProfile
from .common import assign_role, form_error


DjangoUser = get_user_model()


@login_required
@require_GET
def User(request):
    return render(request, "user.html")


@login_required
@require_POST
def User_info(request):
    form = ManagedUserForm(request.POST, creating=True)
    if not form.is_valid():
        return render(request, "user.html", {"error": form_error(form)})

    user = DjangoUser.objects.create_user(
        username=form.cleaned_data["login_id"],
        password=form.cleaned_data["password"],
        is_active=form.cleaned_data["login_status"],
    )
    profile = assign_role(user, form.cleaned_data["role"])
    profile.office_id = form.cleaned_data["office_id"]
    profile.login_status = form.cleaned_data["login_status"]
    profile.create_at = form.cleaned_data.get("create_at") or timezone.localdate()
    profile.updated_at = form.cleaned_data.get("updated_at") or timezone.localdate()
    profile.token = form.cleaned_data.get("token", "")
    profile.save()
    return redirect("User")


def _user_rows():
    rows = []
    profiles = DMSUserProfile.objects.select_related("user", "office", "role")
    for profile in profiles:
        rows.append(
            (
                profile.user_id,
                profile.user.username,
                "********",
                profile.office_id or "",
                profile.role.role if profile.role else "",
                profile.login_status,
                profile.create_at,
                profile.updated_at,
            )
        )
    return rows


@login_required
@require_GET
def User_list(request):
    return render(request, "user_details.html", {"data": _user_rows()})


@login_required
@require_POST
def User_delete(request, id):
    user = get_object_or_404(DjangoUser, pk=id)
    if user == request.user:
        messages.error(request, "You cannot delete the account you are using.")
    else:
        user.delete()
    return redirect("User_list")


@login_required
@require_GET
def User_Edit(request, id):
    profile = get_object_or_404(
        DMSUserProfile.objects.select_related("user", "role"), user_id=id
    )
    data = (
        profile.user_id,
        profile.user.username,
        "",
        profile.office_id or "",
        profile.role.role if profile.role else "",
        profile.login_status,
        profile.create_at.isoformat(),
        profile.updated_at.isoformat(),
    )
    return render(request, "user_update.html", {"data": data})


@login_required
@require_POST
def User_update(request):
    user = get_object_or_404(DjangoUser, pk=request.POST.get("uid"))
    profile, _ = DMSUserProfile.objects.get_or_create(user=user)
    form = ManagedUserForm(request.POST, user=user)
    if not form.is_valid():
        data = (
            user.pk,
            request.POST.get("login_id", user.username),
            "",
            request.POST.get("office_id", profile.office_id or ""),
            request.POST.get("role", profile.role.role if profile.role else ""),
            request.POST.get("login_status", profile.login_status),
            profile.create_at.isoformat(),
            request.POST.get("updated_at", profile.updated_at.isoformat()),
        )
        return render(
            request,
            "user_update.html",
            {"data": data, "error": form_error(form)},
        )

    user.username = form.cleaned_data["login_id"]
    user.is_active = form.cleaned_data["login_status"]
    if form.cleaned_data.get("password"):
        user.set_password(form.cleaned_data["password"])
    user.save()
    profile = assign_role(user, form.cleaned_data["role"])
    profile.office_id = form.cleaned_data["office_id"]
    profile.login_status = form.cleaned_data["login_status"]
    profile.updated_at = form.cleaned_data.get("updated_at") or timezone.localdate()
    profile.save()
    return redirect("User_list")
