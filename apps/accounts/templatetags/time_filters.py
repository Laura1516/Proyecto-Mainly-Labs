from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def format_duration(value):
    """
    Formatea un timedelta para mostrar solo horas:minutos:segundos sin microsegundos
    """
    if not value:
        return "0:00:00"
    
    if isinstance(value, timedelta):
        # Convertir a segundos totales y quitar microsegundos
        total_seconds = int(value.total_seconds())
        
        # Calcular horas, minutos y segundos
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        # Formatear como H:MM:SS
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    
    # Si no es un timedelta, devolver tal como está
    return str(value)

@register.filter
def format_duration_short(value):
    """
    Formatea un timedelta de forma corta (solo horas y minutos si los segundos son 0)
    """
    if not value:
        return "0:00"
    
    if isinstance(value, timedelta):
        # Convertir a segundos totales y quitar microsegundos
        total_seconds = int(value.total_seconds())
        
        # Calcular horas, minutos y segundos
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        # Si no hay segundos, mostrar solo H:MM
        if seconds == 0:
            return f"{hours}:{minutes:02d}"
        else:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
    
    # Si no es un timedelta, devolver tal como está
    return str(value)