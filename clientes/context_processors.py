from datetime import datetime
from django.utils import timezone

def fecha_hora(request):
    fecha_hora_actual = timezone.localtime(timezone.now())
    print(f'Zona Horaria: {timezone.get_current_timezone()}')
    print(f'Fecha y Hora Actual: {fecha_hora_actual}')
    
    return {
        'fecha_formateada': formatear_fecha(fecha_hora_actual),
    }


def formatear_fecha(fecha):
    # Formatear la fecha y hora en el formato deseado
    return fecha.strftime('%d/%m/%Y %I:%M:%S %p')
