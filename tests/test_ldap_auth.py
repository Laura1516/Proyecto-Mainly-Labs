#!/usr/bin/env python

import os
import sys
import django
from django.conf import settings

# Add project path
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

django.setup()

from django.contrib.auth import authenticate

def test_ldap_auth():
    print("Testing LDAP authentication...")
    
    # Test with our test user
    username = "testuser"
    password = "testpass123"
    
    user = authenticate(username=username, password=password)
    
    if user:
        print(f"SUCCESS: Authentication successful for {username}")
        print(f"User details: {user.username}, {user.email}, {user.first_name} {user.last_name}")
        return True
    else:
        print(f"FAILED: Authentication failed for {username}")
        return False

if __name__ == "__main__":
    success = test_ldap_auth()
    sys.exit(0 if success else 1)