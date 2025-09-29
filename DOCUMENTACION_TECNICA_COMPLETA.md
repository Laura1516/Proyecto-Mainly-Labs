# 📚 DOCUMENTACIÓN TÉCNICA COMPLETA - SISTEMA LDAP
**Proyecto: Mainly-labs - Implementación LDAP**  
**Autor: Juan Ramón Fernández**  
**Fecha: 23 de septiembre de 2025**  
**Rama: juanrra_implementacion_ldap**

---

## 🎯 ARQUITECTURA DEL SISTEMA

### Componentes Principales
- **Django 5.2.6**: Framework web principal
- **OpenLDAP**: Servidor de directorio para autenticación
- **django-auth-ldap**: Integración Django-LDAP
- **PostgreSQL**: Base de datos relacional (opcional)

### Estructura del Proyecto
```
apps/
└── accounts/                    # App principal de autenticación
    ├── views.py                 # Lógica de negocio y vistas
    ├── urls.py                  # Rutas URL
    ├── forms.py                 # Formularios personalizados
    ├── models.py                # Modelos de datos
    ├── admin.py                 # Configuración admin Django
    └── templates/               # Plantillas HTML
        ├── admin/               # Templates gestión LDAP
        ├── dashboard/           # Dashboards por rol
        ├── registration/        # Login/registro
        └── home/               # Página principal

project/
├── settings.py                  # Configuración principal
├── urls.py                      # URLs raíz
└── wsgi.py                     # Servidor WSGI

Archivos de configuración:
├── .env                        # Variables de entorno
├── .env.example               # Plantilla configuración
├── requirements.txt           # Dependencias Python
├── LDAP_SETUP.md             # Documentación instalación LDAP
└── admin_config.ldif         # Configuración admin LDAP
```

---

## 🔗 MAPEO FUNCIONALIDAD → CÓDIGO

### 1. 🚪 SISTEMA DE AUTENTICACIÓN

#### Login de Usuarios
**Ubicación**: `apps/accounts/views.py:38-49`
```python
class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = CustomLoginForm

    def get_success_url(self):
        # Redirect basado en rol del usuario
```
**URL**: `apps/accounts/urls.py:15`
```python
path("login/", views.CustomLoginView.as_view(), name="login")
```
**Template**: `apps/accounts/templates/registration/login.html`
**Formulario**: `apps/accounts/forms.py:CustomLoginForm`

#### Logout Personalizado
**Ubicación**: `apps/accounts/views.py:58-68`
```python
def custom_logout_view(request):
    """Logout que acepta GET y POST con mensajes personalizados"""
```
**URL**: `apps/accounts/urls.py:16`
```python
path("logout/", views.custom_logout_view, name="logout")
```

#### Configuración LDAP Backend
**Ubicación**: `project/settings.py:123-126`
```python
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',    # ← Autenticación principal
    'django.contrib.auth.backends.ModelBackend'  # ← Fallback local
]
```

**Configuración LDAP**: `project/settings.py:131-180`
```python
# Conexión LDAP
AUTH_LDAP_SERVER_URI = env("AUTH_LDAP_SERVER_URI", default="ldap://localhost:389")
AUTH_LDAP_BIND_DN = env("AUTH_LDAP_BIND_DN", default="")
AUTH_LDAP_BIND_PASSWORD = env("AUTH_LDAP_BIND_PASSWORD", default="")

# Búsqueda de usuarios
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    env("AUTH_LDAP_USER_DN", default="ou=users,dc=example,dc=com"),
    ldap.SCOPE_SUBTREE,
    env("AUTH_LDAP_USER_FILTER", default="(uid=%(user)s)")
)

# Mapeo atributos LDAP → Django
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn", 
    "email": "mail",
}
```

---

### 2. 👥 GESTIÓN DE USUARIOS LDAP

#### Creación de Usuarios LDAP
**Ubicación**: `apps/accounts/views.py:101-132`
```python
@user_passes_test(is_admin)
def create_ldap_user(request):
    """Vista para crear usuarios en LDAP (solo admins)"""
```
**Función de creación**: `apps/accounts/views.py:135-202`
```python
def create_user_in_ldap(username, first_name, last_name, email, password, role, is_staff):
    """Crea usuario en servidor LDAP con asignación automática de grupos"""
```
**URL**: `apps/accounts/urls.py:47`
```python
path("ldap/create-user/", views.create_ldap_user, name="create_ldap_user")
```
**Template**: `apps/accounts/templates/admin/create_ldap_user.html`
**Formulario**: `apps/accounts/forms.py:LDAPUserCreationForm`

#### Listado de Usuarios LDAP
**Ubicación**: `apps/accounts/views.py:205-235`
```python
@user_passes_test(is_admin)
def list_ldap_users(request):
    """Lista todos los usuarios del directorio LDAP"""
```
**URL**: `apps/accounts/urls.py:48`
```python
path("ldap/list-users/", views.list_ldap_users, name="list_ldap_users")
```
**Template**: `apps/accounts/templates/admin/list_ldap_users.html`

#### Control de Acceso Admin
**Ubicación**: `apps/accounts/views.py:94-96`
```python
def is_admin(user):
    """Verifica si usuario tiene permisos de administrador"""
    return user.is_authenticated and user.role == 'admin'
```

---

### 3. 🏠 PÁGINAS PRINCIPALES

#### Página de Inicio
**Ubicación**: `apps/accounts/views.py:53-55`
```python
def home_view(request):
    return render(request, "home/home.html")
```
**URL**: `apps/accounts/urls.py:19`
```python
path("home/", views.home_view, name="home")
```
**Template**: `apps/accounts/templates/home/home.html`

#### Redirect Raíz
**Ubicación**: `apps/accounts/urls.py:12`
```python
path("", lambda request: HttpResponseRedirect('/home/'), name="root")
```

---

### 4. 📊 SISTEMA DE DASHBOARDS

#### Dashboard Administrador
**Ubicación**: `apps/accounts/views.py:82-84`
```python
@login_required
def admin_dashboard(request):
    return render(request, "dashboard/admin_dashboard.html")
```
**URL**: `apps/accounts/urls.py:43`
**Template**: `apps/accounts/templates/dashboard/admin_dashboard.html`

#### Dashboard HR
**Ubicación**: `apps/accounts/views.py:86-88`
```python
@login_required
def hr_dashboard(request):
    return render(request, "dashboard/hr_dashboard.html")
```
**URL**: `apps/accounts/urls.py:44`

#### Dashboard Técnico
**Ubicación**: `apps/accounts/views.py:90-92`
```python
@login_required
def tech_dashboard(request):
    return render(request, "dashboard/tech_dashboard.html")
```
**URL**: `apps/accounts/urls.py:45`

#### Dashboard Usuario
**Ubicación**: `apps/accounts/views.py:94-96`
```python
@login_required
def user_dashboard(request):
    return render(request, "dashboard/user_dashboard.html")
```
**URL**: `apps/accounts/urls.py:46`

---

### 5. 👤 GESTIÓN DE PERFILES

#### Perfil de Usuario
**Ubicación**: `apps/accounts/views.py:70-80`
```python
@login_required
def profile(request):
    """Vista para editar perfil de usuario"""
```
**URL**: `apps/accounts/urls.py:22`
**Formulario**: `apps/accounts/forms.py:ProfileForm`

#### Registro Tradicional
**Ubicación**: `apps/accounts/views.py:21-30`
```python
class RegisterView(FormView):
    template_name = "registration/registration_form.html"
    form_class = RegistrationForm
```
**URL**: `apps/accounts/urls.py:25`
**Formulario**: `apps/accounts/forms.py:RegistrationForm`

---

### 6. 🔧 FORMULARIOS PERSONALIZADOS

**Ubicación**: `apps/accounts/forms.py`

#### Formulario Login
```python
class CustomLoginForm(AuthenticationForm):
    """Formulario de login personalizado con estilos"""
```

#### Formulario Creación LDAP
```python
class LDAPUserCreationForm(forms.Form):
    """Formulario para crear usuarios en LDAP"""
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[...])
    is_staff = forms.BooleanField(required=False)
```

#### Formulario Registro
```python
class RegistrationForm(UserCreationForm):
    """Formulario de registro con campos adicionales"""
```

#### Formulario Perfil
```python
class ProfileForm(forms.ModelForm):
    """Formulario para editar información del perfil"""
```

---

### 7. 🗄️ ESTRUCTURA DE DATOS LDAP

#### Estructura del Directorio
```
dc=example,dc=com                           # Base DN
├── ou=users,dc=example,dc=com             # Organizational Unit: Usuarios
│   ├── uid=juanrra,ou=users,dc=example,dc=com
│   ├── uid=adminuser,ou=users,dc=example,dc=com
│   └── uid=helen,ou=users,dc=example,dc=com
└── ou=groups,dc=example,dc=com            # Organizational Unit: Grupos
    ├── cn=active,ou=groups,dc=example,dc=com      # Usuarios activos
    ├── cn=admin,ou=groups,dc=example,dc=com       # Administradores
    ├── cn=staff,ou=groups,dc=example,dc=com       # Staff Django
    ├── cn=superuser,ou=groups,dc=example,dc=com   # Superusuarios
    ├── cn=hr,ou=groups,dc=example,dc=com          # Recursos Humanos
    └── cn=tech,ou=groups,dc=example,dc=com        # Técnicos
```

#### Esquema de Usuario LDAP
```ldif
dn: uid=username,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
uid: username                    # Nombre de usuario (único)
cn: Nombre Completo             # Nombre completo del usuario
sn: Apellido                    # Apellido
givenName: Nombre               # Nombre de pila
mail: email@domain.com          # Dirección de correo
userPassword: {SSHA}...         # Contraseña encriptada
```

#### Asignación de Grupos por Rol
**Ubicación**: `apps/accounts/views.py:169-185`
```python
# Lógica de asignación automática de grupos
groups_to_add = ['active']  # Todos los usuarios activos

if role == 'admin':
    groups_to_add.extend(['admin', 'staff', 'superuser'])
elif role == 'hr':
    groups_to_add.append('hr')
elif role == 'tech':
    groups_to_add.extend(['tech', 'staff'])
else:  # user
    groups_to_add.append('user')
```

---

### 8. ⚙️ CONFIGURACIÓN Y VARIABLES

#### Variables de Entorno
**Archivo**: `.env`
```bash
# Django
DJANGO_SECRET_KEY='secret-key'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DB_NAME=mainly_labs_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432

# LDAP - Configuración crucial
AUTH_LDAP_SERVER_URI=ldap://localhost:389
AUTH_LDAP_BIND_DN=cn=admin,dc=example,dc=com
AUTH_LDAP_BIND_PASSWORD=InterNat

# LDAP - Búsqueda de usuarios
AUTH_LDAP_USER_DN=ou=users,dc=example,dc=com
AUTH_LDAP_USER_FILTER=(uid=%(user)s)
AUTH_LDAP_GROUP_DN=ou=groups,dc=example,dc=com
```

#### Dependencias Críticas
**Archivo**: `requirements.txt`
```
Django==5.2.6                  # Framework web
django-auth-ldap==4.6.0        # Integración LDAP
python-ldap==3.4.3             # Cliente LDAP Python
django-environ==0.11.2         # Gestión variables entorno
psycopg2-binary==2.9.7         # Driver PostgreSQL
```

#### Apps Instaladas
**Ubicación**: `project/settings.py:55-74`
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.accounts',        # ← App principal
    'apps.assistance',
    'apps.hr',
    'apps.projects_manager',
    'apps.purchase_order',
    'apps.suggestions',
    'apps.tasks_manager',
    'apps.training_course',
]
```

---

### 9. 🔒 SISTEMA DE SEGURIDAD

#### Decoradores de Seguridad
**Ubicación**: `apps/accounts/views.py`
```python
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required                    # Requiere autenticación
@user_passes_test(is_admin)       # Solo administradores
```

#### Verificación de Permisos
**Ubicación**: `apps/accounts/views.py:94-96`
```python
def is_admin(user):
    """Función para verificar permisos de administrador"""
    return user.is_authenticated and user.role == 'admin'
```

#### Control de Acceso en URLs
**Ubicación**: `apps/accounts/urls.py:47-48`
```python
# Solo admins pueden acceder a gestión LDAP
path("ldap/create-user/", views.create_ldap_user, name="create_ldap_user"),
path("ldap/list-users/", views.list_ldap_users, name="list_ldap_users"),
```

---

### 10. 🎨 TEMPLATES Y UI

#### Estructura de Templates
```
apps/accounts/templates/
├── base_generic.html                      # Layout base común
├── home/
│   └── home.html                         # Página principal
├── registration/
│   ├── login.html                        # Formulario login
│   ├── registration_form.html            # Formulario registro
│   └── profile_form.html                 # Edición perfil
├── dashboard/
│   ├── admin_dashboard.html              # Dashboard admin
│   ├── hr_dashboard.html                 # Dashboard HR
│   ├── tech_dashboard.html               # Dashboard técnico
│   └── user_dashboard.html               # Dashboard usuario
└── admin/
    ├── create_ldap_user.html             # Crear usuario LDAP
    └── list_ldap_users.html              # Listar usuarios LDAP
```

#### Navegación Principal
**Ubicación**: `apps/accounts/templates/base_generic.html`
- Menú responsive con Bootstrap
- Links dinámicos según autenticación
- Breadcrumbs automáticos

---

### 11. 🔄 FLUJOS DE TRABAJO PRINCIPALES

#### Flujo: Login de Usuario
1. **URL**: `/login/` → `CustomLoginView`
2. **Template**: `registration/login.html`
3. **Proceso**: 
   - Django-auth-ldap busca en LDAP
   - Valida credenciales
   - Crea/actualiza usuario Django
   - Redirect basado en rol

#### Flujo: Creación Usuario LDAP
1. **URL**: `/ldap/create-user/` → `create_ldap_user()`
2. **Verificación**: `@user_passes_test(is_admin)`
3. **Template**: `admin/create_ldap_user.html`
4. **Proceso**:
   - Validación formulario
   - Conexión LDAP admin
   - Creación entrada usuario
   - Asignación grupos automática

#### Flujo: Navegación Dashboard
1. **Login exitoso** → `get_success_url()`
2. **Evaluación rol** → Redirect apropiado
3. **Dashboard específico** → Funciones según permisos

---

### 12. 🐛 DEPURACIÓN Y LOGS

#### Comandos de Verificación LDAP
```bash
# Ver usuarios LDAP
ldapsearch -x -LLL -b "ou=users,dc=example,dc=com"

# Ver grupos LDAP  
ldapsearch -x -LLL -b "ou=groups,dc=example,dc=com"

# Verificar usuario específico
ldapsearch -x -LLL -b "ou=users,dc=example,dc=com" "(uid=username)"

# Estado servicio LDAP
systemctl status slapd
```

#### Logs Django
```python
# En views.py - Agregar para debug
import logging
logger = logging.getLogger(__name__)

def create_ldap_user(request):
    logger.info(f"Admin {request.user.username} creando usuario LDAP")
```

#### Variables Debug
**Ubicación**: `project/settings.py`
```python
DEBUG = env('DEBUG', default=False)
LOGGING = {
    # Configuración logs...
}
```

---

### 13. 📋 COMANDOS ADMINISTRATIVOS

#### Gestión Django
```bash
# Migraciones
python manage.py makemigrations
python manage.py migrate

# Servidor desarrollo
python manage.py runserver

# Shell Django
python manage.py shell

# Superusuario Django (backup)
python manage.py createsuperuser
```

#### Gestión LDAP
```bash
# Configurar admin LDAP
sudo slappasswd                                    # Generar hash contraseña
sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f admin_config.ldif

# Backup/Restore LDAP
slapcat > backup.ldif                             # Backup
sudo systemctl stop slapd                        # Para servicio
sudo rm -rf /var/lib/ldap/*                      # Limpia datos
sudo slapadd < backup.ldif                       # Restaura
sudo systemctl start slapd                       # Inicia servicio
```

---

### 14. 📊 MÉTRICAS Y MONITOREO

#### Usuarios Activos
**Comando**: 
```bash
ldapsearch -x -LLL -b "ou=users,dc=example,dc=com" | grep "dn:" | wc -l
```

#### Verificación Conectividad
**Ubicación**: `apps/accounts/management/commands/test_ldap.py`
```python
# Comando personalizado Django para test LDAP
python manage.py test_ldap
```

#### Health Check LDAP
```bash
# Test conexión básica
ldapsearch -x -LLL -b "dc=example,dc=com" "(objectClass=*)" | head -5

# Test autenticación admin  
ldapsearch -D "cn=admin,dc=example,dc=com" -w InterNat -b "dc=example,dc=com"
```

---

## 🎯 RESUMEN EJECUTIVO

### Funcionalidades Implementadas ✅
- **Autenticación LDAP** centralizada y robusta
- **Gestión completa usuarios** vía web interface
- **Sistema roles** con dashboards específicos
- **Integración perfecta** LDAP ↔ Django
- **Interface administrativa** intuitiva
- **Seguridad multicapa** con decoradores

### Archivos Críticos del Sistema
1. **`apps/accounts/views.py`** - Lógica principal (248 líneas)
2. **`project/settings.py`** - Configuración LDAP
3. **`apps/accounts/urls.py`** - Rutas del sistema
4. **`apps/accounts/forms.py`** - Formularios personalizados
5. **`.env`** - Variables de configuración

### Próximas Mejoras Sugeridas
- **Eliminación usuarios LDAP** desde web interface
- **Edición masiva** de usuarios
- **Auditoría completa** de cambios
- **API REST** para integración externa
- **Dashboard analítico** con métricas

---

**📅 Última actualización**: 23 de septiembre de 2025  
**🔧 Mantenido por**: Juan Ramón Fernández  
**📧 Contacto**: aljuanrra914@gmail.com  
**🌐 Repositorio**: https://github.com/itprogerspain/Mainly-labs/tree/juanrra_implementacion_ldap

---