from django.dispatch import receiver
from django_auth_ldap.backend import populate_user
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@receiver(populate_user)
def ldap_user_role_mapping(sender, user=None, ldap_user=None, **kwargs):
    """
    Signal handler to map LDAP groups to user roles.
    This is called after an LDAP user is authenticated and their attributes are populated.
    """
    if user and ldap_user:
        # Get LDAP groups for this user
        ldap_groups = ldap_user.group_names
        logger.info(f"LDAP groups for user {user.username}: {ldap_groups}")
        
        # Default role
        user.role = 'user'
        
        # Check group membership and assign role accordingly
        # Priority: admin > hr > tech > user
        if hasattr(settings, 'AUTH_LDAP_PROFILE_FLAGS_BY_GROUP'):
            role_groups = settings.AUTH_LDAP_PROFILE_FLAGS_BY_GROUP.get('role', {})
            
            # Extract group names from DN strings
            admin_group = extract_group_name(role_groups.get('admin', ''))
            hr_group = extract_group_name(role_groups.get('hr', ''))
            tech_group = extract_group_name(role_groups.get('tech', ''))
            user_group = extract_group_name(role_groups.get('user', ''))
            
            if admin_group in ldap_groups:
                user.role = 'admin'
            elif hr_group in ldap_groups:
                user.role = 'hr'
            elif tech_group in ldap_groups:
                user.role = 'tech'
            elif user_group in ldap_groups:
                user.role = 'user'
        
        # Save the updated user
        user.save()
        logger.info(f"Assigned role '{user.role}' to user {user.username}")


def extract_group_name(group_dn):
    """
    Extract the group name from a DN string.
    Example: 'cn=admin,ou=groups,dc=example,dc=com' -> 'admin'
    """
    if not group_dn:
        return ''
    
    try:
        # Split by comma and find the part starting with 'cn='
        parts = group_dn.split(',')
        for part in parts:
            part = part.strip()
            if part.lower().startswith('cn='):
                return part[3:]  # Remove 'cn=' prefix
    except Exception as e:
        logger.error(f"Error extracting group name from {group_dn}: {e}")
    
    return ''