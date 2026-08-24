from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login as auth_login,
    logout as auth_logout,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from ..forms import LoginForm, SignupForm
from ..models import DMSUserProfile
from .common import assign_role, form_error


DjangoUser = get_user_model()


@require_GET
def login(request):
    if request.user.is_authenticated:
        return redirect("Home")
    return render(request, "login.html")


@require_GET
def signup(request):
    if request.user.is_authenticated:
        return redirect("Home")
    return render(request, "signup.html")


@require_POST
def select(request):
    form = LoginForm(request.POST)
    if not form.is_valid():
        return render(request, "login.html", {"error": form_error(form)})

    username = form.cleaned_data["username"]
    password = form.cleaned_data["password"]
    selected_role = form.cleaned_data["Role"]
    user = authenticate(request, username=username, password=password)
    if user is None:
        return render(request, "login.html", {"error": "Invalid username or password."})

    profile = DMSUserProfile.objects.filter(user=user).select_related("role").first()
    actual_role = profile.role.role if profile and profile.role else None
    if not (user.is_superuser and selected_role == "Admin") and actual_role != selected_role:
        return render(
            request,
            "login.html",
            {"error": "The selected role does not match this user account."},
        )

    auth_login(request, user)
    return redirect("Home")


@require_POST
def Insert(request):
    form = SignupForm(request.POST)
    if not form.is_valid():
        return render(request, "signup.html", {"error": form_error(form)})

    user = DjangoUser.objects.create_user(
        username=form.cleaned_data["username"],
        password=form.cleaned_data["password"],
    )
    assign_role(user, form.cleaned_data["Role"])
    messages.success(request, "Signup completed. Please log in.")
    return redirect("login")


@require_GET
def logout_view(request):
    auth_logout(request)
    return redirect("login")


@login_required
@require_GET
def Home(request):
    return render(request, "main.html")
