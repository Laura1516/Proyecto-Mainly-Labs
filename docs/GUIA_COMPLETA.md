# Guia completa: Despliegue, configuracion y operacion (Docker + LDAP + Django)

Este documento unifica y reemplaza la documentacion anterior: `README-DOCKER.md`, `DOCKER_LDAP_SETUP_COMPLETO.md`, `INSTRUCCIONES-COMPAÑEROS.md`, `LDAP_SETUP.md`, `DOCUMENTACION_TECNICA_COMPLETA.md`, `RESUMEN_TRABAJO_19_SEPTIEMBRE_2025.md`.

Indice
- Introduccion
- Requisitos y versiones
- Mapa completo de carpetas y descripcion de cada elemento
- Puesta en marcha rapida
- Servicios Docker: detalle, redes y volumenes
- Accesos y credenciales de ejemplo
- Operacion diaria (comandos utiles)
- Variables de entorno: referencia completa y ejemplos
- Configuracion de autenticacion LDAP en Django
- Estructura y datos de LDAP esperados
- Arquitectura Django: apps, vistas, urls, templates, signals, formularios
- Flujos funcionales detallados
- Seguridad y control de acceso
- Procedimientos operativos recomendados
- Troubleshooting extendido
- Comandos administrativos y depuracion
- Referencia tecnica (mapa funcionalidad → codigo)
- Notas tecnicas y proximas mejoras

Introduccion
Aplicacion Django integrada con autenticacion LDAP, dockerizada para un arranque reproducible. Incluye gestion de usuarios LDAP desde la interfaz y asignacion automatica de roles basada en grupos LDAP.

Requisitos y versiones
- Docker 24+ y Docker Compose v2
- Python 3.11+ dentro del contenedor
- Django 5.x en el proyecto
- Servicios Docker: web (Django), db (PostgreSQL), ldap (OpenLDAP), phpldapadmin

Mapa completo de carpetas y descripcion de cada elemento
```
MAINLY-LABS-MUSK/
├── apps/                                # Conjunto de aplicaciones Django
│   ├── __init__.py
│   ├── accounts/                        # App principal de autenticacion y perfiles
│   │   ├── __init__.py
│   │   ├── admin.py                     # Registro de modelos en admin Django
│   │   ├── apps.py                      # Configuracion de la app (carga de signals)
│   │   ├── forms.py                     # Formularios (login, registro, LDAP user)
│   │   ├── ldap_signals.py              # Asignacion de roles tras autenticacion LDAP
│   │   ├── management/
│   │   │   ├── __init__.py
│   │   │   └── commands/
│   │   │       ├── __init__.py
│   │   │       └── test_ldap.py         # Comando para probar autenticacion LDAP
│   │   ├── migrations/                  # Migraciones de la app
│   │   │   ├── __init__.py
│   │   │   └── 0001_initial.py
│   │   ├── models.py                    # Modelos (usuario/rol si aplica)
│   │   ├── templates/                   # Plantillas de la app
│   │   │   ├── admin/
│   │   │   │   ├── create_ldap_user.html
│   │   │   │   └── list_ldap_users.html
│   │   │   ├── base/
│   │   │   │   ├── base_dashboard.html
│   │   │   │   ├── base_form.html
│   │   │   │   └── base_message.html
│   │   │   ├── dashboard/
│   │   │   │   ├── admin_dashboard.html
│   │   │   │   ├── hr_dashboard.html
│   │   │   │   ├── tech_dashboard.html
│   │   │   │   └── user_dashboard.html
│   │   │   ├── home/
│   │   │   │   └── home.html
│   │   │   ├── profile/
│   │   │   │   ├── profile_detail.html
│   │   │   │   ├── profile_edit.html
│   │   │   │   └── profile_update.html
│   │   │   └── registration/
│   │   │       ├── login.html
│   │   │       ├── password_change_done.html
│   │   │       ├── password_change_form.html
│   │   │       ├── password_reset_form.html
│   │   │       └── registration_form.html
│   │   ├── tests.py
│   │   ├── urls.py                      # Rutas de la app (login, logout, ldap/*)
│   │   └── views.py                     # Vistas y logica LDAP (crear/listar usuarios)
│   ├── assistance/                      # App de asistencia (plantilla base)
│   ├── hr/                              # App de recursos humanos (plantilla base)
│   ├── projects_manager/                # App de gestion de proyectos (plantilla base)
│   ├── purchase_order/                  # App de pedidos de compra (plantilla base)
│   ├── suggestions/                     # App de sugerencias (plantilla base)
│   ├── tasks_manager/                   # App de tareas (plantilla base)
│   └── training_course/                 # App de formacion (plantilla base)
├── db.sqlite3                           # Base de datos local (si se usa SQLite)
├── docker/
│   ├── Dockerfile                       # Imagen de la app Django
│   └── docker-compose.yml               # Orquestacion de servicios
├── docs/
│   └── GUIA_COMPLETA.md                 # Este documento
├── ldap/
│   ├── admin_config.ldif                # Config LDAP admin del servidor
│   ├── init_ldap_data.ldif              # Usuarios/grupos de ejemplo para carga inicial
│   └── ldap_groups.ldif                 # Definicion de grupos para roles y permisos
├── project/
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py                        # Si aplica tareas asinc (plantilla)
│   ├── settings.py                      # Configuracion Django (LDAP, DB, apps, templates)
│   ├── urls.py                          # Rutas globales
│   └── wsgi.py
├── requirements.txt                     # Dependencias Python
├── scripts/
│   ├── fix_admin_role.py                # Asegura rol de administrador en Django
│   └── wait-for-ldap.sh                 # Espera LDAP antes de iniciar servicios dependientes
├── manage.py                            # Entrypoint de gestion Django
└── README.md                            # Resumen y enlace a la guia
```

Puesta en marcha rapida
1) Obtener el codigo
```bash
git clone <tu_repositorio>
cd <tu_repositorio>
```
2) Variables de entorno (opcional)
```bash
cp .env.example .env
```
3) Levantar servicios
```bash
docker-compose up -d
```
4) Migraciones
```bash
docker-compose exec web python manage.py migrate
```
5) Cargar datos LDAP de ejemplo
```bash
docker-compose exec ldap ldapadd -x -D "cn=admin,dc=example,dc=com" -w InterNat -f /ldap/init_ldap_data.ldif
```
6) Ajustar rol de administrador (opcional)
```bash
docker-compose exec web python /scripts/fix_admin_role.py
```
7) Verificar estado
```bash
docker-compose ps
```

Servicios Docker: detalle, redes y volumenes
- web: servicio Django
  - Depende de ldap y db
  - Expone puerto 8000 (mapeado a host)
  - Monta el codigo de la app y usa variables de entorno de `.env`
- db: base de datos PostgreSQL
  - Puerto interno 5432
  - Volumen de datos persistente
- ldap: OpenLDAP
  - Puertos 389 (interno) y 1389 (externo opcional)
  - Volumen de datos para `cn=config` y base de datos
  - Carga inicial mediante archivos LDIF en `ldap/`
- phpldapadmin: interfaz web para administrar LDAP
  - Puerto 8080 en host

Redes
- Red de aplicacion predefinida por Compose para comunicacion entre servicios (por ejemplo `app-network`).

Volumenes tipicos
- `db_data`: datos de PostgreSQL
- `ldap_data` y `ldap_config`: datos y configuracion de OpenLDAP

Accesos y credenciales de ejemplo
- Aplicacion: http://localhost:8000
- phpLDAPAdmin: http://localhost:8080
- Admin LDAP: `cn=admin,dc=example,dc=com` / `InterNat`
- Usuarios ejemplo (si se cargan ldif):
  - admin / admin123
  - testuser / testpass123

Operacion diaria (comandos utiles)
```bash
# Estado y logs
docker-compose ps
docker-compose logs web
docker-compose logs ldap
docker-compose logs -f web
# Ciclo de vida
docker-compose down
docker-compose restart web
docker-compose build && docker-compose up -d
# Base de datos
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
# Pruebas rapidas
docker-compose exec web python test_ldap_auth.py
```

Variables de entorno: referencia completa y ejemplos
Ejemplo `.env` orientativo:
```bash
# Django
DJANGO_SECRET_KEY=changeme
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DB_NAME=mainly_labs_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432

# LDAP basico
AUTH_LDAP_SERVER_URI=ldap://ldap:389
AUTH_LDAP_BIND_DN=cn=admin,dc=example,dc=com
AUTH_LDAP_BIND_PASSWORD=InterNat

# Busqueda de usuarios
AUTH_LDAP_USER_DN=ou=users,dc=example,dc=com
AUTH_LDAP_USER_FILTER=(uid=%(user)s)
AUTH_LDAP_GROUP_DN=ou=groups,dc=example,dc=com

# Mapeo de grupos a roles
AUTH_LDAP_GROUP_ADMIN=cn=admin,ou=groups,dc=example,dc=com
AUTH_LDAP_GROUP_HR=cn=hr,ou=groups,dc=example,dc=com
AUTH_LDAP_GROUP_TECH=cn=tech,ou=groups,dc=example,dc=com
AUTH_LDAP_GROUP_USER=cn=user,ou=groups,dc=example,dc=com

# Flags de usuario por grupo (opcional)
AUTH_LDAP_GROUP_ACTIVE=cn=active,ou=groups,dc=example,dc=com
AUTH_LDAP_GROUP_STAFF=cn=staff,ou=groups,dc=example,dc=com
AUTH_LDAP_GROUP_SUPERUSER=cn=superuser,ou=groups,dc=example,dc=com
```

Configuracion de autenticacion LDAP en Django
Dependencias (ya incluidas): `django-auth-ldap`, `python-ldap`.

Backends en `project/settings.py`:
```python
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

Mapeo de atributos LDAP → Django
- uid → username
- givenName → first_name
- sn → last_name
- mail → email

Asignacion de roles por grupos
- Prioridad: admin > hr > tech > user
- Asignacion automatica mediante `ldap_signals.py` despues de autenticar

Estructura y datos de LDAP esperados
```
dc=example,dc=com
├── ou=users
│   ├── uid=adminuser,ou=users,dc=example,dc=com
│   └── uid=testuser,ou=users,dc=example,dc=com
└── ou=groups
    ├── cn=active,ou=groups,dc=example,dc=com
    ├── cn=staff,ou=groups,dc=example,dc=com
    ├── cn=superuser,ou=groups,dc=example,dc=com
    ├── cn=admin,ou=groups,dc=example,dc=com
    ├── cn=hr,ou=groups,dc=example,dc=com
    ├── cn=tech,ou=groups,dc=example,dc=com
    └── cn=user,ou=groups,dc=example,dc=com
```

Arquitectura Django: apps, vistas, urls, templates, signals, formularios
- Apps principales:
  - `apps.accounts`: autenticacion, gestion LDAP, dashboards, perfiles
  - Otras apps (`assistance`, `hr`, `projects_manager`, `purchase_order`, `suggestions`, `tasks_manager`, `training_course`) como modulos funcionales base
- Vistas destacadas (`apps/accounts/views.py`):
  - `create_ldap_user(request)`: crea usuario en LDAP con atributos minimos y lo asigna a grupos segun el rol
  - `list_ldap_users(request)`: lista entradas en `ou=users` y muestra atributos basicos
  - `custom_logout_view(request)`: logout compatible con GET/POST, redirige a `home`
- URLs (`apps/accounts/urls.py`):
  - Raiz redirige a `/home/`
  - Prefijo `/ldap/` para gestion de usuarios LDAP
  - `login`, `logout`, dashboards por rol
- Templates (`apps/accounts/templates/...`):
  - `admin/create_ldap_user.html`, `admin/list_ldap_users.html`, `dashboard/*`, `home/home.html`, `registration/*`
- Signals (`apps/accounts/ldap_signals.py`):
  - Tras autenticacion, asigna `user.role` segun pertenencia a grupos
- Formularios (`apps/accounts/forms.py`):
  - `LDAPUserCreationForm` con validaciones (nombre, apellidos, email, rol, staff, contrasena minima, confirmacion, formato username)

Flujos funcionales detallados
1) Autenticacion de usuario:
- Usuario envía credenciales en `/login/`
- Se intenta autenticacion via LDAP
- Si LDAP autentica: se mapean atributos, se asigna rol via signals y se redirige al dashboard segun rol
- Si LDAP falla: fallback a autenticacion local de Django (si aplica)

2) Creacion de usuario LDAP (solo administracion):
- Se valida formulario
- Se conecta al servidor LDAP usando `AUTH_LDAP_BIND_*`
- Se crea entrada `uid=<username>,ou=users,...` con `inetOrgPerson`
- Se agregan miembros a grupos: `active` y segun rol (`admin`, `hr`, `tech` o `user`)

Seguridad y control de acceso
- Decoradores: `@login_required` y `@user_passes_test(is_admin)`
- Politicas:
  - Rutas `/ldap/*` solo para administracion
  - Dashboards por rol con navegacion contextual

Procedimientos operativos recomendados
- Antes de crear usuarios: verificar conectividad a LDAP y credenciales de bind
- Tras cambios de variables: reiniciar `web` y verificar logs de `django_auth_ldap`
- Para cambios de estructura LDAP: actualizar DN en variables y en funciones de asignacion de grupos

Troubleshooting extendido
- Docker sin permisos (Linux): agregar usuario a grupo `docker`, cerrar sesion y reentrar
- Puerto 8000 ocupado: modificar mapeo de puertos en Compose (por ejemplo `8001:8000`)
- LDAP no inicia:
  - `docker-compose logs ldap`
  - Revisar validez de LDIF y permisos de volúmenes
  - Reiniciar solo LDAP: `docker-compose restart ldap`
- Django no conecta a LDAP:
  - Probar conectividad desde `web`: `nc -z ldap 389` (o `openssl s_client` si TLS)
  - Revisar variables `AUTH_LDAP_*`
- Contraseñas LDAP mal codificadas:
  - En altas de usuario, enviar la contraseña en UTF-8 sin doble codificacion; LDAP aplica hashing segun configuracion
- Templates no encontrados:
  - Verificar `TEMPLATES['DIRS']` y rutas `render(...)`
- Conflicto de rutas con `/admin/` de Django:
  - Mantener prefijo `/ldap/` para modulos propios

Comandos administrativos y depuracion
```bash
# Django
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
python manage.py shell
python manage.py createsuperuser

# LDAP (ejemplos)
ldapsearch -x -LLL -b "ou=users,dc=example,dc=com"
ldapsearch -x -LLL -b "ou=groups,dc=example,dc=com"
ldapadd -x -D "cn=admin,dc=example,dc=com" -w InterNat -f /ldap/ldap_groups.ldif
ldapdelete -x -D "cn=admin,dc=example,dc=com" -w InterNat "uid=USERNAME,ou=users,dc=example,dc=com"
```

Referencia tecnica (mapa funcionalidad → codigo)
- Configuracion LDAP y backends: `project/settings.py`
- Rutas principales y protecciones: `apps/accounts/urls.py`
- Vistas: `apps/accounts/views.py`
- Formularios: `apps/accounts/forms.py`
- Templates: `apps/accounts/templates/...`
- Señales: `apps/accounts/ldap_signals.py`

Notas tecnicas y proximas mejoras
- Tecnologias: Django, django-auth-ldap, python-ldap, Bootstrap
- Mejoras sugeridas: edicion/eliminacion de usuarios, reseteo de contraseñas, auditoria, paginacion/filtros, TLS en produccion para LDAP, pruebas integradas y healthchecks en Compose

---

Anexos y explicaciones ampliadas

Ejemplo comentado de docker-compose.yml
```yaml
version: "3.9"
services:
  web:                       # Servicio Django
    build:                   # Construye imagen desde Dockerfile
      context: .
      dockerfile: docker/Dockerfile
    container_name: app_web
    env_file:
      - .env                 # Variables de entorno centralizadas
    ports:
      - "8000:8000"         # Host:Contenedor
    depends_on:
      - db
      - ldap
    volumes:
      - ./:/app              # Monta el codigo para desarrollo
    command: ["python", "manage.py", "runserver", "0.0.0.0:8000"]

  db:                        # PostgreSQL
    image: postgres:15
    container_name: app_db
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data

  ldap:                      # OpenLDAP
    image: osixia/openldap:1.5.0
    container_name: app_ldap
    environment:
      LDAP_ORGANISATION: "Example"
      LDAP_DOMAIN: "example.com"
      LDAP_ADMIN_PASSWORD: "InterNat"
    ports:
      - "1389:389"          # Puerto 389 expuesto en 1389 del host
    volumes:
      - ldap_data:/var/lib/ldap
      - ldap_config:/etc/ldap/slapd.d
      - ./ldap:/container/service/slapd/assets/config/bootstrap/ldif/custom

  phpldapadmin:              # UI para administrar LDAP
    image: osixia/phpldapadmin:0.9.0
    container_name: app_phpldapadmin
    environment:
      PHPLDAPADMIN_LDAP_HOSTS: ldap
    ports:
      - "8080:80"
    depends_on:
      - ldap

volumes:
  db_data:
  ldap_data:
  ldap_config:
```

Ejemplo comentado de Dockerfile
```Dockerfile
# Imagen base con Python
FROM python:3.11-slim

# Variables de entorno para Python (no generar pyc y salida sin buffer)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Paquetes del sistema necesarios para python-ldap y Pillow
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Instala dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia el codigo (en desarrollo, el volumen sobreescribe)
COPY . .

# Puerto expuesto por Django dev server
EXPOSE 8000

# Comando por defecto (puede ser sobreescrito por docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

Esquema LDAP y ejemplos LDIF
- Un usuario tipico `inetOrgPerson` requiere atributos minimos: `uid`, `cn`, `sn`, `givenName`, `mail`, `userPassword`.
- Un grupo tipico `groupOfNames` requiere `cn` y al menos un `member` con DN completo.

Usuario de ejemplo (LDIF)
```ldif
dn: uid=jdoe,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
uid: jdoe
cn: John Doe
sn: Doe
givenName: John
mail: jdoe@example.com
userPassword: password123
```

Grupo de ejemplo (LDIF)
```ldif
dn: cn=tech,ou=groups,dc=example,dc=com
objectClass: groupOfNames
cn: tech
description: Technical role
member: uid=jdoe,ou=users,dc=example,dc=com
```

Matrices de entorno: desarrollo vs produccion
- Desarrollo
  - `DEBUG=True`
  - Montaje de volumen con codigo fuente
  - Base de datos local o contenedorizada con datos efimeros
  - Puertos expuestos en host (8000, 8080, 1389)
- Produccion
  - `DEBUG=False`
  - Imagenes versionadas y escaneo de vulnerabilidades
  - Volumenes persistentes y backups programados
  - TLS en LDAP y en la aplicacion (reverse proxy Nginx/Traefik)
  - Variables de entorno en un gestor seguro (Azure Key Vault, AWS Secrets Manager)

Seguridad: consideraciones
- Credenciales de bind LDAP: mantener fuera del repositorio y rotar periodicamente
- TLS para LDAP: activar `AUTH_LDAP_START_TLS` o LDAPS segun politicas
- Cabeceras de seguridad Django: `SECURE_*` en produccion
- Separacion de roles: uso de grupos LDAP para limitar accesos y vistas
- Logging de acceso y auditoria: almacenar en backend centralizado

Backups y restauracion
- PostgreSQL
  - Backup: `pg_dump -h db -U ${DB_USER} ${DB_NAME} > backup.sql`
  - Restore: `psql -h db -U ${DB_USER} ${DB_NAME} < backup.sql`
- OpenLDAP
  - Backup: `slapcat > backup.ldif` (dentro del contenedor ldap)
  - Restore: parar slapd, limpiar directorio de datos, `slapadd < backup.ldif`, reiniciar
- Verificar integridad: pruebas de login y presencia de grupos/usuarios clave

Monitoreo y logs
- Django
  - Configurar `LOGGING` con handlers a consola y a archivo/servicio externo
  - Niveles `INFO/ERROR` en produccion, `DEBUG` solo en desarrollo
- Docker
  - `docker-compose logs -f web` para seguimiento en tiempo real
  - Integracion con Loki/ELK para centralizacion
- LDAP
  - Revisar `docker-compose logs ldap`
  - Habilitar nivel de log mas detallado al diagnosticar

Rendimiento y buenas practicas
- Consultas a LDAP: filtrar por `uid` y limitar el arbol de busqueda
- Pool de conexiones a DB y configuracion de `CONN_MAX_AGE` en Django
- Cachear datos estaticos en front (Nginx) y usar compresion
- Evitar doble codificacion de contraseñas en altas LDAP
- Paginar listados de usuarios si el directorio es grande

FAQ
- ¿Puedo usar LDAP externo en lugar del contenedor?
  - Si. Ajustar `AUTH_LDAP_SERVER_URI` a la URL del servidor y validar conectividad desde `web`.
- ¿Como cambio puertos sin editar codigo?
  - Modificar mapeos en `docker-compose.yml` y reiniciar servicios.
- ¿Que pasa si el usuario existe en Django pero no en LDAP?
  - La autenticacion intenta LDAP primero; si falla y existe backend local, se podra autenticar localmente si hay credenciales validas.

Glosario
- Bind DN: DN de la cuenta de servicio usada para consultar/modificar LDAP
- DN (Distinguished Name): identificador unico jerarquico de una entrada LDAP
- LDIF: formato de intercambio de datos LDAP
- GroupOfNames: objeto LDAP que mantiene miembros por DN
- inetOrgPerson: objeto LDAP para representar personas/usuarios
