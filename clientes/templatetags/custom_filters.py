from django import template
from datetime import datetime

register = template.Library()

@register.filter(name='formatear_fecha')
def formatear_fecha(fecha):
    return fecha.strftime('%d/%m/%Y %I:%M:%S %p')
