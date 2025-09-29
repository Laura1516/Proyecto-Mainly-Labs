from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from django.conf import settings
import logging

# Set up logging to show LDAP debug information
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('django_auth_ldap')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class Command(BaseCommand):
    help = 'Test LDAP authentication with a username and password'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='LDAP username to test')
        parser.add_argument('password', type=str, help='LDAP password to test')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        
        self.stdout.write(f"Testing LDAP authentication for user: {username}")
        self.stdout.write(f"LDAP Server: {getattr(settings, 'AUTH_LDAP_SERVER_URI', 'Not configured')}")
        
        try:
            # Test authentication
            user = authenticate(username=username, password=password)
            
            if user:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Authentication successful for {username}")
                )
                self.stdout.write(f"User details:")
                self.stdout.write(f"  - Username: {user.username}")
                self.stdout.write(f"  - Email: {user.email}")
                self.stdout.write(f"  - First name: {user.first_name}")
                self.stdout.write(f"  - Last name: {user.last_name}")
                self.stdout.write(f"  - Role: {getattr(user, 'role', 'N/A')}")
                self.stdout.write(f"  - Is active: {user.is_active}")
                self.stdout.write(f"  - Is staff: {user.is_staff}")
                self.stdout.write(f"  - Is superuser: {user.is_superuser}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ Authentication failed for {username}")
                )
                self.stdout.write("Possible causes:")
                self.stdout.write("  - Invalid username or password")
                self.stdout.write("  - LDAP server connection issues")
                self.stdout.write("  - Incorrect LDAP configuration")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Error during authentication: {str(e)}")
            )
            self.stdout.write("Check your LDAP configuration and server connectivity")