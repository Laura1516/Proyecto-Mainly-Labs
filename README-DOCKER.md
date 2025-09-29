# 🐳 Quick Start: Docker LDAP Setup

## 🚀 Para empezar (2 minutos)

```bash
# 1. Clonar el repositorio
git clone https://github.com/JuanRRaFdez/Mainly-labs.git
cd Mainly-labs

# 2. Crear archivo de configuración
cp .env.example .env

# 3. Levantar todos los servicios
docker-compose up -d

# 4. Configurar base de datos
docker-compose exec web python manage.py migrate

# 5. Cargar usuarios LDAP
docker-compose exec ldap ldapadd -x -D "cn=admin,dc=example,dc=com" -w InterNat -f /ldap/init_ldap_data.ldif

# 6. ¡Acceder a la aplicación!
# Web: http://localhost:8000
# LDAP Admin: http://localhost:8080
```

## ✅ Verificar que funciona

```bash
# Ver estado de los servicios
docker-compose ps

# Debe mostrar todos los servicios como "Up"
# Si algo falla, revisar logs:
docker-compose logs web
```

## 👤 Usuarios de Prueba

**Admin**: 
- Usuario: `admin`
- Contraseña: `admin123`
- Dashboard: Admin completo

**Usuario de prueba**: 
- Usuario: `testuser`  
- Contraseña: `testpass123`
- Dashboard: Usuario normal

## 🔧 Comandos Útiles

```bash
# Parar servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Ver logs en tiempo real
docker-compose logs -f web

# Reconstruir si hay cambios
docker-compose build
docker-compose up -d
```

## ❓ ¿Problemas?

1. **Puerto ocupado**: Cambiar puertos en `docker-compose.yml`
2. **LDAP no inicia**: `docker-compose logs ldap`
3. **Django error**: `docker-compose logs web`

## 📋 URLs de Acceso

- **Aplicación Web**: http://localhost:8000
- **Admin LDAP**: http://localhost:8080  
  - Usuario: `cn=admin,dc=example,dc=com`
  - Contraseña: `InterNat`

---

**Todo funciona automáticamente con Docker - sin instalar nada local!** 🎉