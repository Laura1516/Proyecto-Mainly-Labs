from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from . import views
from .forms import (
    CustomPasswordResetForm,
    CustomPasswordChangeForm,
)

urlpatterns = [
    # Root redirect to home
    path("", lambda request: HttpResponseRedirect('/home/'), name="root"),
    
    # Login / Logout
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.custom_logout_view, name="logout"),

    # Home
    path("home/", views.home_view, name="home"),

    # Profile
    path("profile/", views.profile, name="profile"),

    # Registration
    path("register/", views.RegisterView.as_view(), name="register"),

    # Password reset (request email)
    path("password_reset/", auth_views.PasswordResetView.as_view(
        template_name="registration/password_reset_form.html",
        form_class=CustomPasswordResetForm
    ), name="password_reset"),

    # Password change
    path("password_change/", auth_views.PasswordChangeView.as_view(
        template_name="registration/password_change_form.html",
        form_class=CustomPasswordChangeForm
    ), name="password_change"),
    path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="registration/password_change_done.html"
    ), name="password_change_done"),

    # Dashboards by role
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/hr/", views.hr_dashboard, name="hr_dashboard"),
    path("dashboard/tech/", views.tech_dashboard, name="tech_dashboard"),
    path("dashboard/user/", views.user_dashboard, name="user_dashboard"),
    
    # LDAP User Management (Admin only)
    path("ldap/create-user/", views.create_ldap_user, name="create_ldap_user"),
    path("ldap/list-users/", views.list_ldap_users, name="list_ldap_users"),
]

