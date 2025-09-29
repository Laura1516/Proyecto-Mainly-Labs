# Configuración de Autenticación LDAP

Este proyecto está configurado para usar autenticación LDAP además de la autenticación estándar de Django.

## Dependencias Instaladas

- `django-auth-ldap`: Backend de autenticación LDAP para Django
- `python-ldap`: Biblioteca de Python para LDAP

## Configuración

### 1. Variables de Entorno

Copia el archivo `.env.example` a `.env` y configura las siguientes variables:

```bash
# Servidor LDAP
AUTH_LDAP_SERVER_URI=ldap://tu-servidor-ldap:389

# Credenciales para bind (cuenta de servicio)
AUTH_LDAP_BIND_DN=cn=admin,dc=ejemplo,dc=com
AUTH_LDAP_BIND_PASSWORD=tu-password-de-bind

# Configuración de búsqueda de usuarios
AUTH_LDAP_USER_DN=ou=users,dc=ejemplo,dc=com
AUTH_LDAP_USER_FILTER=(uid=%(user)s)
AUTH_LDAP_GROUP_DN=ou=groups,dc=ejemplo,dc=com

# Mapeo de grupos para permisos
AUTH_LDAP_GROUP_ACTIVE=cn=active,ou=groups,dc=ejemplo,dc=com
AUTH_LDAP_GROUP_STAFF=cn=staff,ou=groups,dc=ejemplo,dc=com
AUTH_LDAP_GROUP_SUPERUSER=cn=superuser,ou=groups,dc=ejemplo,dc=com

# Mapeo de grupos para roles
AUTH_LDAP_GROUP_ADMIN=cn=admin,ou=groups,dc=ejemplo,dc=com
AUTH_LDAP_GROUP_HR=cn=hr,ou=groups,dc=ejemplo,dc=com
AUTH_LDAP_GROUP_TECH=cn=tech,ou=groups,dc=ejemplo,dc=com
AUTH_LDAP_GROUP_USER=cn=user,ou=groups,dc=ejemplo,dc=com
```

### 2. Backend de Autenticación

El sistema está configurado para intentar autenticación LDAP primero, y luego la autenticación local:

```python
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

### 3. Mapeo de Atributos

Los atributos LDAP se mapean a campos del usuario Django:

- `uid` → `username`
- `givenName` → `first_name`
- `sn` → `last_name`
- `mail` → `email`

### 4. Mapeo de Roles

Los grupos LDAP se mapean automáticamente a roles del sistema:

- Grupo `admin` → Rol `admin`
- Grupo `hr` → Rol `hr`
- Grupo `tech` → Rol `tech`
- Grupo `user` → Rol `user`

## Uso

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### Prueba de Configuración

Para probar que la configuración LDAP funciona correctamente:

```bash
python manage.py test_ldap username password
```

Este comando intentará autenticar al usuario y mostrará información detallada sobre el proceso.

### Iniciar Sesión

Los usuarios pueden iniciar sesión usando:
- Su nombre de usuario LDAP y contraseña LDAP
- Sus credenciales locales de Django (si tienen cuenta local)

## Estructura LDAP Esperada

El sistema espera una estructura LDAP como esta:

```
dc=ejemplo,dc=com
├── ou=users
│   ├── uid=juan,ou=users,dc=ejemplo,dc=com
│   ├── uid=maria,ou=users,dc=ejemplo,dc=com
│   └── ...
└── ou=groups
    ├── cn=admin,ou=groups,dc=ejemplo,dc=com
    ├── cn=hr,ou=groups,dc=ejemplo,dc=com
    ├── cn=tech,ou=groups,dc=ejemplo,dc=com
    ├── cn=user,ou=groups,dc=ejemplo,dc=com
    ├── cn=active,ou=groups,dc=ejemplo,dc=com
    ├── cn=staff,ou=groups,dc=ejemplo,dc=com
    └── cn=superuser,ou=groups,dc=ejemplo,dc=com
```

## Configuración TLS (Opcional)

Para conexiones seguras, descomenta y configura estas líneas en `settings.py`:

```python
AUTH_LDAP_START_TLS = True
AUTH_LDAP_CONNECTION_OPTIONS[ldap.OPT_X_TLS_REQUIRE_CERT] = ldap.OPT_X_TLS_NEVER
```

## Troubleshooting

1. **Error de conexión**: Verifica que el servidor LDAP esté accesible
2. **Autenticación fallida**: Verifica credenciales y filtros de búsqueda
3. **Roles no asignados**: Verifica que los grupos LDAP existan y el usuario sea miembro

## Logs

Para ver logs detallados de LDAP, usa el comando de prueba o configura logging en Django:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_auth_ldap': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```