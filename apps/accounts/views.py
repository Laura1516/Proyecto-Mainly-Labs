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
from django.db import models
from .models import CustomUser

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

@login_required
def user_fichaje(request):
    from .models import RegistroFichaje, Proyecto
    from django.utils import timezone
    from django.utils.timezone import localtime
    import datetime
    import locale
    
    # Configurar localización para fechas en español
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')  # Windows
        except:
            pass  # Si no se puede configurar, usar el formato por defecto
    
    today = timezone.now().date()
    
    # Obtener o crear registro de hoy
    registro_hoy, created = RegistroFichaje.objects.get_or_create(
        usuario=request.user,
        fecha=today,
        defaults={'jornada': 'presencial'}
    )
    
    # Obtener proyectos activos
    proyectos = Proyecto.objects.filter(activo=True)
    
    # Obtener registros históricos (últimos 10 días)
    registros_historicos = RegistroFichaje.objects.filter(
        usuario=request.user
    ).order_by('-fecha')[:10]
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'fichar_entrada':
            if not registro_hoy.proyecto:
                messages.error(request, 'Debes seleccionar un proyecto antes de fichar la entrada')
            elif not registro_hoy.hora_entrada:
                registro_hoy.hora_entrada = localtime(timezone.now()).time()
                registro_hoy.save()
                messages.success(request, f'Entrada fichada a las {registro_hoy.hora_entrada.strftime("%H:%M")} para el proyecto {registro_hoy.proyecto.nombre}')
            else:
                messages.warning(request, 'Ya has fichado la entrada hoy')
                
        elif action == 'fichar_salida':
            if not registro_hoy.proyecto:
                messages.error(request, 'Debes seleccionar un proyecto antes de fichar la salida')
            elif registro_hoy.hora_entrada and not registro_hoy.hora_salida:
                registro_hoy.hora_salida = localtime(timezone.now()).time()
                registro_hoy.save()
                messages.success(request, f'Salida fichada a las {registro_hoy.hora_salida.strftime("%H:%M")} para el proyecto {registro_hoy.proyecto.nombre}')
            elif not registro_hoy.hora_entrada:
                messages.error(request, 'Debes fichar la entrada primero')
            else:
                messages.warning(request, 'Ya has fichado la salida hoy')
                
        elif action == 'actualizar_proyecto':
            proyecto_id = request.POST.get('proyecto')
            jornada = request.POST.get('jornada')
            
            if proyecto_id:
                try:
                    proyecto = Proyecto.objects.get(id=proyecto_id)
                    registro_hoy.proyecto = proyecto
                except Proyecto.DoesNotExist:
                    messages.error(request, 'Proyecto no válido')
                    
            if jornada:
                registro_hoy.jornada = jornada
                
            registro_hoy.save()
            messages.success(request, 'Información actualizada correctamente')
        
        return redirect('user_fichaje')
    
    # Formatear fecha en español
    meses = [
        '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ]
    fecha_formateada = f"{today.day} de {meses[today.month]} de {today.year}"
    
    context = {
        'registro_hoy': registro_hoy,
        'proyectos': proyectos,
        'registros': registros_historicos,
        'today_date': fecha_formateada,
        'puede_fichar_entrada': not registro_hoy.hora_entrada and registro_hoy.proyecto,
        'puede_fichar_salida': registro_hoy.hora_entrada and not registro_hoy.hora_salida and registro_hoy.proyecto,
        'necesita_proyecto': not registro_hoy.proyecto,
    }
    
    return render(request, "fichaje/user_fichaje.html", context)


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


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def list_django_users(request):
    """
    List all users from Django database
    """
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Obtener todos los usuarios de Django
    users = User.objects.all().order_by('username')
    
    # Preparar datos para el template
    user_list = []
    for user in users:
        user_info = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'role': getattr(user, 'role', 'user'),  # Rol personalizado si existe
        }
        user_list.append(user_info)
    
    return render(request, 'admin/list_django_users.html', {
        'users': user_list,
        'total_users': users.count()
    })


# Admin Reporting Views
@login_required
@user_passes_test(lambda u: u.role == 'admin')
def admin_reports_dashboard(request):
    """
    Dashboard principal de reportes para el administrador
    """
    from .models import RegistroFichaje, Proyecto
    from django.db.models import Count, Sum, Avg
    from datetime import timedelta
    
    # Estadísticas generales
    total_proyectos = Proyecto.objects.filter(activo=True).count()
    total_usuarios_activos = CustomUser.objects.filter(is_active=True).count()
    
    # Registros del último mes
    from django.utils import timezone
    hace_30_dias = timezone.now().date() - timedelta(days=30)
    
    registros_mes = RegistroFichaje.objects.filter(fecha__gte=hace_30_dias)
    total_registros_mes = registros_mes.count()
    
    # Proyectos más activos (por número de registros)
    proyectos_activos = Proyecto.objects.annotate(
        num_registros=Count('registrofichaje', filter=models.Q(registrofichaje__fecha__gte=hace_30_dias))
    ).filter(activo=True).order_by('-num_registros')[:5]
    
    # Usuarios más activos
    usuarios_activos = CustomUser.objects.annotate(
        num_fichajes=Count('fichajes', filter=models.Q(fichajes__fecha__gte=hace_30_dias))
    ).filter(is_active=True).order_by('-num_fichajes')[:5]
    
    context = {
        'total_proyectos': total_proyectos,
        'total_usuarios_activos': total_usuarios_activos,
        'total_registros_mes': total_registros_mes,
        'proyectos_activos': proyectos_activos,
        'usuarios_activos': usuarios_activos,
    }
    
    return render(request, 'admin/reports_dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def admin_projects_report(request):
    """
    Reporte de todos los proyectos con estadísticas
    """
    from .models import RegistroFichaje, Proyecto
    from django.db.models import Count, Sum, Q
    from datetime import datetime, timedelta
    
    # Filtros opcionales
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # Construir filtros
    filtros = Q(activo=True)
    filtros_registros = Q()
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            filtros_registros &= Q(registrofichaje__fecha__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            filtros_registros &= Q(registrofichaje__fecha__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # Obtener proyectos con estadísticas
    proyectos = Proyecto.objects.filter(filtros).annotate(
        total_trabajadores=Count('registrofichaje__usuario', distinct=True, filter=filtros_registros),
        total_registros=Count('registrofichaje', filter=filtros_registros),
        total_horas=Sum('registrofichaje__horas_trabajadas', filter=filtros_registros)
    ).order_by('-total_registros')
    
    context = {
        'proyectos': proyectos,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'admin/projects_report.html', context)


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def admin_project_detail(request, project_id):
    """
    Detalle de un proyecto específico con trabajadores asignados
    """
    from .models import RegistroFichaje, Proyecto
    from django.db.models import Sum, Count, Q
    from datetime import datetime
    
    try:
        proyecto = Proyecto.objects.get(id=project_id)
    except Proyecto.DoesNotExist:
        messages.error(request, 'Proyecto no encontrado')
        return redirect('admin_projects_report')
    
    # Filtros opcionales
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    filtros_registros = Q(proyecto=proyecto)
    fecha_desde_obj = None
    fecha_hasta_obj = None
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            filtros_registros &= Q(fecha__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            filtros_registros &= Q(fecha__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # Construir filtros para anotaciones de CustomUser
    filtro_base = Q(fichajes__proyecto=proyecto)
    if fecha_desde_obj:
        filtro_base &= Q(fichajes__fecha__gte=fecha_desde_obj)
    if fecha_hasta_obj:
        filtro_base &= Q(fichajes__fecha__lte=fecha_hasta_obj)
    
    # Trabajadores en este proyecto con sus estadísticas
    trabajadores_stats = CustomUser.objects.filter(
        fichajes__proyecto=proyecto
    ).annotate(
        total_horas=Sum('fichajes__horas_trabajadas', 
                       filter=filtro_base & Q(fichajes__horas_trabajadas__isnull=False)),
        total_dias=Count('fichajes', filter=filtro_base),
        horas_presencial=Sum('fichajes__horas_trabajadas', 
                           filter=filtro_base & Q(fichajes__jornada='presencial') & 
                                 Q(fichajes__horas_trabajadas__isnull=False)),
        horas_remoto=Sum('fichajes__horas_trabajadas', 
                        filter=filtro_base & Q(fichajes__jornada='remoto') & 
                               Q(fichajes__horas_trabajadas__isnull=False)),
        horas_desplazamiento=Sum('fichajes__horas_trabajadas', 
                               filter=filtro_base & Q(fichajes__jornada='desplazamiento') & 
                                     Q(fichajes__horas_trabajadas__isnull=False))
    ).distinct().order_by('-total_horas')
    
    # Registros detallados del proyecto
    registros = RegistroFichaje.objects.filter(filtros_registros).select_related(
        'usuario', 'proyecto'
    ).order_by('-fecha', '-hora_entrada')[:50]  # Últimos 50 registros
    
    context = {
        'proyecto': proyecto,
        'trabajadores_stats': trabajadores_stats,
        'registros': registros,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'admin/project_detail.html', context)


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def admin_workers_report(request):
    """
    Reporte de todos los trabajadores con estadísticas
    """
    from .models import RegistroFichaje
    from django.db.models import Count, Sum, Q, Avg
    from datetime import datetime, timedelta
    
    # Filtros opcionales
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    filtros = Q()
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            filtros &= Q(fichajes__fecha__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            filtros &= Q(fichajes__fecha__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # Trabajadores con estadísticas
    trabajadores = CustomUser.objects.filter(is_active=True).annotate(
        total_dias_trabajados=Count('fichajes', filter=filtros),
        total_horas=Sum('fichajes__horas_trabajadas', filter=filtros),
        proyectos_trabajados=Count('fichajes__proyecto', distinct=True, filter=filtros),
        horas_promedio_dia=Avg('fichajes__horas_trabajadas', filter=filtros),
        dias_presencial=Count('fichajes', filter=filtros & Q(fichajes__jornada='presencial')),
        dias_remoto=Count('fichajes', filter=filtros & Q(fichajes__jornada='remoto')),
        dias_desplazamiento=Count('fichajes', filter=filtros & Q(fichajes__jornada='desplazamiento'))
    ).order_by('-total_horas')
    
    context = {
        'trabajadores': trabajadores,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'admin/workers_report.html', context)


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def admin_worker_detail(request, user_id):
    """
    Detalle de un trabajador específico con todos sus proyectos y horarios
    """
    from .models import RegistroFichaje, Proyecto
    from django.db.models import Sum, Count, Q
    from datetime import datetime
    
    try:
        trabajador = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Trabajador no encontrado')
        return redirect('admin_workers_report')
    
    # Filtros opcionales
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    filtros_registros = Q(usuario=trabajador)
    fecha_desde_obj = None
    fecha_hasta_obj = None
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            filtros_registros &= Q(fecha__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            filtros_registros &= Q(fecha__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    # Construir filtros para anotaciones de Proyecto
    filtro_base = Q(registrofichaje__usuario=trabajador)
    if fecha_desde_obj:
        filtro_base &= Q(registrofichaje__fecha__gte=fecha_desde_obj)
    if fecha_hasta_obj:
        filtro_base &= Q(registrofichaje__fecha__lte=fecha_hasta_obj)
    
    # Proyectos del trabajador con estadísticas
    proyectos_stats = Proyecto.objects.filter(
        registrofichaje__usuario=trabajador
    ).annotate(
        total_horas=Sum('registrofichaje__horas_trabajadas', 
                       filter=filtro_base & Q(registrofichaje__horas_trabajadas__isnull=False)),
        total_dias=Count('registrofichaje', filter=filtro_base),
        horas_presencial=Sum('registrofichaje__horas_trabajadas', 
                           filter=filtro_base & Q(registrofichaje__jornada='presencial') & 
                                 Q(registrofichaje__horas_trabajadas__isnull=False)),
        horas_remoto=Sum('registrofichaje__horas_trabajadas', 
                        filter=filtro_base & Q(registrofichaje__jornada='remoto') & 
                               Q(registrofichaje__horas_trabajadas__isnull=False)),
        horas_desplazamiento=Sum('registrofichaje__horas_trabajadas', 
                               filter=filtro_base & Q(registrofichaje__jornada='desplazamiento') & 
                                     Q(registrofichaje__horas_trabajadas__isnull=False))
    ).distinct().order_by('-total_horas')
    
    # Registros detallados del trabajador (horarios diarios)
    registros = RegistroFichaje.objects.filter(filtros_registros).select_related(
        'proyecto'
    ).order_by('-fecha')[:30]  # Últimos 30 días
    
    # Estadísticas generales
    stats_generales = RegistroFichaje.objects.filter(
        filtros_registros & Q(horas_trabajadas__isnull=False)
    ).aggregate(
        total_horas=Sum('horas_trabajadas'),
        total_dias=Count('id'),
        total_proyectos=Count('proyecto', distinct=True)
    )
    
    context = {
        'trabajador': trabajador,
        'proyectos_stats': proyectos_stats,
        'registros': registros,
        'stats': stats_generales,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'admin/worker_detail.html', context)