# 📋 INSTRUCCIONES PARA COMPAÑEROS DE EQUIPO

## 🎯 Qué vas a encontrar
He dockerizado completamente la aplicación Django con autenticación LDAP. **Todo funciona automáticamente** sin instalaciones locales.

## 📥 Pasos para usar el sistema

### 1. Obtener el código
```bash
git clone https://github.com/JuanRRaFdez/Mainly-labs.git
cd Mainly-labs
```
> **Nota**: El código Docker ya está en la rama main

### 2. Configurar variables de entorno
```bash
# Crear archivo de configuración
cp .env.example .env
```
> **Nota**: Los valores por defecto funcionan perfectamente para desarrollo

### 3. Levantar el sistema completo
```bash
docker-compose up -d
```
> **⏱️ Primera vez**: Puede tardar 2-3 minutos descargando imágenes

### 4. Configurar base de datos Django
```bash
# Ejecutar migraciones para crear las tablas
docker-compose exec web python manage.py migrate
```
> **Importante**: Esto crea las tablas necesarias en PostgreSQL

### 5. Cargar usuarios de prueba en LDAP
```bash
# Esperar a que LDAP esté listo (unos 30 segundos)
docker-compose exec ldap ldapadd -x -D "cn=admin,dc=example,dc=com" -w InterNat -f /ldap/init_ldap_data.ldif
```
> **Nota**: Este comando carga los usuarios admin y testuser automáticamente

### 6. Verificar y corregir roles de usuario
```bash
# Verificar que el usuario admin tenga el rol correcto
docker-compose exec web python fix_admin_role.py
```
> **Importante**: Esto asegura que admin vaya al dashboard de administrador

### 7. Verificar que todo funciona
```bash
docker-compose ps
```
Deberías ver:
```
NOMBRE      ESTADO
web         Up
db          Up  
ldap        Up
phpldapadmin Up
```

### 8. Acceder a la aplicación
- **Aplicación**: http://localhost:8000
- **Usuario**: `admin` / **Contraseña**: `admin123`

## 🌟 ¿Qué tienes disponible?

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **App Django** | http://localhost:8000 | Aplicación principal |
| **phpLDAPAdmin** | http://localhost:8080 | Gestión visual del LDAP |

## 👥 Usuarios disponibles

| Usuario | Contraseña | Rol | Dashboard |
|---------|------------|-----|-----------|
| admin | admin123 | Administrador | Admin completo |
| testuser | testpass123 | Usuario normal | Dashboard usuario |

## 🔧 Comandos frecuentes

```bash
# Ver logs si algo falla
docker-compose logs web
docker-compose logs ldap

# Parar todo
docker-compose down

# Reiniciar solo un servicio
docker-compose restart web

# Ver estado en tiempo real
docker-compose logs -f web
```

## ⚠️ Posibles problemas y soluciones

### Permisos de Docker (Linux)
Si al ejecutar `docker-compose` te da error de permisos:
```bash
# Opción 1: Usar sudo temporalmente
sudo docker-compose up -d
sudo docker-compose ps

# Opción 2: Arreglar permisos permanentemente
sudo usermod -aG docker $USER
sudo systemctl restart docker
# Luego cerrar terminal y abrir nueva (o logout/login)
```

### Puerto 8000 ocupado
```bash
# En docker-compose.yml cambiar:
ports:
  - "8001:8000"  # Cambiar 8000 por 8001
```

### LDAP no inicia
```bash
# Ver logs específicos
docker-compose logs ldap
# Reiniciar LDAP
docker-compose restart ldap
```

### Base de datos no conecta
```bash
# Reiniciar servicios en orden
docker-compose down
docker-compose up -d
```

## 📞 Contacto
Si algo no funciona, contacta a **Juan** - tiene toda la documentación técnica detallada.

---

**🎉 El sistema funciona completamente sin configuraciones adicionales!**  
*Solo necesitas Docker instalado en tu PC*