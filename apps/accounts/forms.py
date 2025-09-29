# forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
    PasswordChangeForm,
)
from django.contrib.auth.password_validation import password_validators_help_text_html

# Get custom user model
CustomUser = get_user_model()


# Registration form (username + password + password confirmation)
class RegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre de usuario',
            'class': 'form-control',
            'autocomplete': 'username'
        })
    )
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo electrónico',
            'class': 'form-control',
            'autocomplete': 'email'
        })
    )
    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repite la contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def clean(self):
        # Validate that passwords match
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        # Save the user with the hashed password
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user




# Login form
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="",
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Usuario',
            'class': 'form-control',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'form-control',
            'autocomplete': 'current-password'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password']


# Registration form
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'placeholder': 'Usuario',
            'class': 'form-control',
            'autocomplete': 'username'
        })
    )
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo electrónico',
            'class': 'form-control',
            'autocomplete': 'email'
        })
    )
    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repite la contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")


# Password reset (request email)
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo electrónico',
            'class': 'form-control',
            'autocomplete': 'email'
        })
    )


# Set new password (after visiting reset link)
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nueva contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    new_password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repite la nueva contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )


# Change password (user is logged in)
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña actual',
            'class': 'form-control',
            'autocomplete': 'current-password'
        })
    )
    new_password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nueva contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    new_password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repite la nueva contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )


# Profile edit form
class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'placeholder': 'Usuario',
            'class': 'form-control',
            'autocomplete': 'username'
        })
    )
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo electrónico',
            'class': 'form-control',
            'autocomplete': 'email'
        })
    )
    avatar = forms.ImageField(
        label="Avatar",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email")


# LDAP User Creation Form
class LDAPUserCreationForm(forms.Form):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('hr', 'Recursos Humanos'),
        ('tech', 'Técnico'),
        ('user', 'Usuario'),
    ]
    
    username = forms.CharField(
        label="Nombre de usuario",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: jdoe',
            'autocomplete': 'username'
        }),
        help_text="El nombre de usuario para acceder al sistema"
    )
    
    first_name = forms.CharField(
        label="Nombre",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Juan',
            'autocomplete': 'given-name'
        })
    )
    
    last_name = forms.CharField(
        label="Apellidos",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Pérez García',
            'autocomplete': 'family-name'
        })
    )
    
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: juan.perez@empresa.com',
            'autocomplete': 'email'
        })
    )
    
    password = forms.CharField(
        label="Contraseña",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'autocomplete': 'new-password'
        }),
        help_text="La contraseña debe tener al menos 8 caracteres"
    )
    
    confirm_password = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite la contraseña',
            'autocomplete': 'new-password'
        })
    )
    
    role = forms.ChoiceField(
        label="Rol del usuario",
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text="El rol determina los permisos y accesos del usuario"
    )
    
    is_staff = forms.BooleanField(
        label="Usuario staff",
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Los usuarios staff pueden acceder al panel de administración"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Las contraseñas no coinciden")
        
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data['username']
        # Validar que el username solo contenga caracteres válidos para LDAP
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', username):
            raise forms.ValidationError(
                "El nombre de usuario solo puede contener letras, números, puntos, guiones y guiones bajos"
            )
        return username
