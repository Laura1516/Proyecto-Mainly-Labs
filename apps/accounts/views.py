from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.contrib.auth import logout
import ldap
from django.conf import settings

from .forms import (
    CustomLoginForm,
    ProfileForm,
    RegistrationForm,
    LDAPUserCreationForm,
)



# RegisterView handles new user registration using the custom three-field form
class RegisterView(FormView):
    template_name = "registration/registration_form.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        # Save the new user instance if the form is valid
        form.save()
        return super().form_valid(form)



# Custom login view with role-based redirect
class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = CustomLoginForm

    def get_success_url(self):
        user = self.request.user

        if user.role == "admin":
            return reverse("admin_dashboard")
        elif user.role == "hr":
            return reverse("hr_dashboard")
        elif user.role == "tech":
            return reverse("tech_dashboard")
        else:
            return reverse("user_dashboard")


# Home page view
def home_view(request):
    return render(request, "home/home.html")


# Custom logout view that handles both GET and POST
def custom_logout_view(request):
    """
    Custom logout view that accepts both GET and POST requests
    and redirects to home page after logout
    """
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'Has cerrado sesión exitosamente. ¡Hasta pronto, {username}!')
    else:
        messages.info(request, 'No había ninguna sesión activa.')
    
    return redirect('home')

# Profile edit view (login required)
@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
        messages.error(request, "Please correct the errors.")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "registration/profile_form.html", {"form": form})

# Dashboards
@login_required
def admin_dashboard(request):
    return render(request, "dashboard/admin_dashboard.html")

@login_required
def hr_dashboard(request):
    return render(request, "dashboard/hr_dashboard.html")

@login_required
def tech_dashboard(request):
    return render(request, "dashboard/tech_dashboard.html")

@login_required
def user_dashboard(request):
    return render(request, "dashboard/user_dashboard.html")


# Helper function to check if user is admin
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


# LDAP User Management Views
@user_passes_test(is_admin)
def create_ldap_user(request):
    if request.method == 'POST':
        form = LDAPUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Create user in LDAP
                username = form.cleaned_data['username']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                role = form.cleaned_data['role']
                is_staff = form.cleaned_data['is_staff']
                
                # Create user in LDAP server
                success = create_user_in_ldap(
                    username, first_name, last_name, email, password, role, is_staff
                )
                
                if success:
                    messages.success(
                        request, 
                        f'Usuario {username} creado exitosamente en LDAP. Ya puede iniciar sesión.'
                    )
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Error al crear el usuario en LDAP. Revise los logs.')
            except Exception as e:
                messages.error(request, f'Error inesperado: {str(e)}')
    else:
        form = LDAPUserCreationForm()
    
    return render(request, 'admin/create_ldap_user.html', {'form': form})


def create_user_in_ldap(username, first_name, last_name, email, password, role, is_staff):
    """
    Create a new user in the LDAP server
    """
    try:
        # Connect to LDAP server
        ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
        
        # User DN
        user_dn = f"uid={username},ou=users,dc=example,dc=com"
        
        # User attributes - LDAP handles password encoding automatically
        user_attrs = [
            ('objectClass', [b'inetOrgPerson']),
            ('uid', [username.encode('utf-8')]),
            ('cn', [f"{first_name} {last_name}".encode('utf-8')]),
            ('sn', [last_name.encode('utf-8')]),
            ('givenName', [first_name.encode('utf-8')]),
            ('mail', [email.encode('utf-8')]),
            ('userPassword', [password.encode('utf-8')]),  # No base64 encoding needed
        ]
        
        # Add user to LDAP
        ldap_conn.add_s(user_dn, user_attrs)
        
        # Add user to groups based on role and permissions
        groups_to_add = ['active']  # All users are active by default
        
        if role == 'admin':
            groups_to_add.extend(['admin', 'staff', 'superuser'])
        elif role == 'hr':
            groups_to_add.append('hr')
        elif role == 'tech':
            groups_to_add.extend(['tech', 'staff'])
        else:  # user
            groups_to_add.append('user')
        
        if is_staff and role not in ['admin', 'tech']:
            groups_to_add.append('staff')
        
        # Add user to groups
        for group in groups_to_add:
            try:
                group_dn = f"cn={group},ou=groups,dc=example,dc=com"
                mod_attrs = [(ldap.MOD_ADD, 'member', [user_dn.encode('utf-8')])]
                ldap_conn.modify_s(group_dn, mod_attrs)
            except ldap.TYPE_OR_VALUE_EXISTS:
                # User already in group, ignore
                pass
        
        ldap_conn.unbind_s()
        return True
        
    except ldap.ALREADY_EXISTS:
        raise Exception(f"El usuario {username} ya existe en LDAP")
    except ldap.INVALID_CREDENTIALS:
        raise Exception("Credenciales LDAP inválidas para crear usuario")
    except ldap.SERVER_DOWN:
        raise Exception("No se puede conectar al servidor LDAP")
    except Exception as e:
        raise Exception(f"Error al crear usuario en LDAP: {str(e)}")


@user_passes_test(is_admin)
def list_ldap_users(request):
    """
    List all users from LDAP
    """
    try:
        # Connect to LDAP server
        ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
        
        # Search for users
        search_filter = "(objectClass=inetOrgPerson)"
        search_base = "ou=users,dc=example,dc=com"
        
        result = ldap_conn.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter)
        
        users = []
        for dn, attrs in result:
            if dn:  # Skip empty results
                user_info = {
                    'dn': dn,
                    'username': attrs.get('uid', [b''])[0].decode('utf-8'),
                    'name': attrs.get('cn', [b''])[0].decode('utf-8'),
                    'email': attrs.get('mail', [b''])[0].decode('utf-8'),
                    'surname': attrs.get('sn', [b''])[0].decode('utf-8'),
                }
                users.append(user_info)
        
        ldap_conn.unbind_s()
        return render(request, 'admin/list_ldap_users.html', {'users': users})
        
    except Exception as e:
        messages.error(request, f'Error al obtener usuarios LDAP: {str(e)}')
        return redirect('admin_dashboard')


def usuaroios_django():
    pass