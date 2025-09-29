#!/usr/bin/env python3

# Script para verificar y corregir el rol del usuario admin
# Ejecutar con: docker-compose exec web python fix_admin_role.py

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
sys.path.append('/app')
django.setup()

from apps.accounts.models import CustomUser

def main():
    print("=== VERIFICACIÓN DE USUARIOS ===")
    
    # Listar todos los usuarios
    users = CustomUser.objects.all()
    print(f"\nUsuarios en la base de datos: {users.count()}")
    
    for user in users:
        print(f"- Usuario: {user.username}, Email: {user.email}, Rol: {user.role}")
    
    # Verificar usuario admin específicamente
    try:
        admin_user = CustomUser.objects.get(username='admin')
        print(f"\n=== USUARIO ADMIN ENCONTRADO ===")
        print(f"Username: {admin_user.username}")
        print(f"Email: {admin_user.email}")
        print(f"Rol actual: {admin_user.role}")
        print(f"Is active: {admin_user.is_active}")
        print(f"Is staff: {admin_user.is_staff}")
        print(f"Is superuser: {admin_user.is_superuser}")
        
        # Corregir el rol si está incorrecto
        if admin_user.role != 'admin':
            print(f"\n🔧 CORRIGIENDO ROL: {admin_user.role} -> admin")
            admin_user.role = 'admin'
            admin_user.save()
            print("✅ Rol corregido!")
        else:
            print("✅ El rol ya es correcto")
            
    except CustomUser.DoesNotExist:
        print("\n❌ Usuario 'admin' no encontrado en la base de datos")
        print("El usuario se creará automáticamente al hacer login por primera vez")
    
    print("\n=== FIN VERIFICACIÓN ===")

if __name__ == '__main__':
    main()