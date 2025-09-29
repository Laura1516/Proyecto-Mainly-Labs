from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    
    def ready(self):
        # Import signals when the app is ready
        try:
            import apps.accounts.ldap_signals
        except ImportError:
            pass  # LDAP not available, skip signals