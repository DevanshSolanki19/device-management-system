from django.contrib.auth.models import Group

from ..models import DMSUserProfile, Role


def form_error(form):
    return " ".join(
        f"{field.replace('_', ' ').title()}: {' '.join(errors)}"
        for field, errors in form.errors.items()
    )


def assign_role(user, role_name):
    role, _ = Role.objects.get_or_create(role=role_name)
    group, _ = Group.objects.get_or_create(name=role_name)
    user.groups.set([group])
    profile, _ = DMSUserProfile.objects.get_or_create(user=user)
    profile.role = role
    profile.save(update_fields=["role"])
    return profile
