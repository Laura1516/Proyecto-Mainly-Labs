from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from datetime import datetime, timedelta


# Custom manager to handle user and superuser creation
class CustomManagerUser(UserManager):
    def create_user(self, username, email, password, **extra_fields):
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("role", "superadmin")
        return super().create_superuser(username, email, password, **extra_fields)


# Extended user model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('tech', 'Technician'),
        ('user', 'User'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )

    email = models.EmailField(max_length=100, unique=True, blank=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    avatar = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
        default="profiles/default.jpg"
    )

    def __str__(self):
        return self.username

    objects = CustomManagerUser()


# Modelo para proyectos
class Proyecto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"


# Modelo para registro de fichajes
class RegistroFichaje(models.Model):
    JORNADA_CHOICES = [
        ('presencial', 'Presencial'),
        ('remoto', 'Remoto'),
        ('desplazamiento', 'Desplazamiento'),
    ]

    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='fichajes')
    fecha = models.DateField(default=timezone.now)
    hora_entrada = models.TimeField(null=True, blank=True)
    hora_salida = models.TimeField(null=True, blank=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.SET_NULL, null=True, blank=True)
    jornada = models.CharField(max_length=20, choices=JORNADA_CHOICES, default='presencial')
    
    # Campos calculados
    horas_trabajadas = models.DurationField(null=True, blank=True)
    completo = models.BooleanField(default=False)  # True si tiene entrada y salida
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def calcular_horas(self):
        """Calcula las horas trabajadas entre entrada y salida"""
        if self.hora_entrada and self.hora_salida:
            entrada_datetime = datetime.combine(self.fecha, self.hora_entrada)
            salida_datetime = datetime.combine(self.fecha, self.hora_salida)
            
            # Si la salida es menor que la entrada, asumimos que es del día siguiente
            if salida_datetime < entrada_datetime:
                salida_datetime += timedelta(days=1)
            
            self.horas_trabajadas = salida_datetime - entrada_datetime
            self.completo = True
        else:
            self.horas_trabajadas = None
            self.completo = False

    def save(self, *args, **kwargs):
        self.calcular_horas()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha}"

    class Meta:
        verbose_name = "Registro de Fichaje"
        verbose_name_plural = "Registros de Fichaje"
        unique_together = ('usuario', 'fecha')  # Un registro por usuario por día
        ordering = ['-fecha', '-hora_entrada']
