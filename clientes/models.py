from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profiles', null=True, blank=True)

class Cliente(models.Model):
    ORIGEN_CHOICES = [
        ('pagina_web', 'Página web'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('meet', 'Meet'),
        ('contacto_referencial', 'Contacto Referencial'),
        ('marketplace', 'Marketplace'),
        ('publicidad_pagada', 'Publicidad Pagada'),
        ('otros', 'Otros'),
    ]

    SEGUIMIENTO_CHOICES = [
        ('informacion_enviada', 'Información Enviada'),
        ('en_negociacion', 'cliente interesado'),
        ('pendiente_por_llamar', 'Pendiente por Llamar'),
        ('no_contesta', 'No Contesta'),
        ('no_interesado', 'No Interesado'),
        ('por_enviar_deposito', 'Por Enviar Depósito'),
        ('venta_exitoso', 'Venta Exitosa'),
    ]

    MOTIVO_COMPRA_CHOICES = [
        ('inversion', 'Inversión'),
        ('vivienda', 'Vivienda'),
        ('otro', 'Otro'),
    ]
    CIUDADES_PERU = [
        ('amazonas', 'Amazonas'),
        ('ancash', 'Ancash'),
        ('apurimac', 'Apurimac'),
        ('arequipa', 'Arequipa'),
        ('ayacucho', 'Ayacucho'),
        ('cajamarca', 'Cajamarca'),
        ('callao', 'Callao'),
        ('cusco', 'Cusco'),
        ('huancavelica', 'Huancavelica'),
        ('huanuco', 'Huánuco'),
        ('ica', 'Ica'),
        ('junin', 'Junín'),
        ('la_libertad', 'La Libertad'),
        ('lambayeque', 'Lambayeque'),
        ('lima', 'Lima'),
        ('loreto', 'Loreto'),
        ('madre_de_dios', 'Madre De Dios'),
        ('moquegua', 'Moquegua'),
        ('pasco', 'Pasco'),
        ('piura', 'Piura'),
        ('puno', 'Puno'),
        ('san_martin', 'San Martin'),
        ('tacna', 'Tacna'),
        ('tumbes', 'Tumbes'),
        ('ucayali', 'Ucayali'),
        ('otro', 'Otro'),
    ]

    nombre_completo = models.CharField(max_length=100)
    dni = models.CharField(max_length=15, blank=True, null=True)
    lugar_de_origen = models.CharField(max_length=100, choices=CIUDADES_PERU, default='ica')
    celular = models.CharField(max_length=15)
    descripcion = models.TextField(blank=True, null=True)
    origen_del_prospecto = models.CharField(max_length=50, choices=ORIGEN_CHOICES)
    asesor_coordinador = models.ForeignKey(User, on_delete=models.CASCADE)
    seguimiento = models.CharField(max_length=50, choices=SEGUIMIENTO_CHOICES)
    motivo_de_compra = models.CharField(max_length=50, choices=MOTIVO_COMPRA_CHOICES, blank=True, null=True)
    fecha_de_creacion = models.DateTimeField(auto_now_add=True)
    fecha_de_actualizacion = models.DateTimeField(auto_now=True)

class Reporte(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha_de_creacion = models.DateTimeField(auto_now_add=True)
    fecha_de_actualizacion = models.DateTimeField(auto_now=True)

class Asesor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    grupo_coordinador = models.ForeignKey('Coordinador', on_delete=models.CASCADE)

    def __str__(self):
        return f'Asesor: {self.usuario.username}'

    def num_ventas_exitosas(self):
        return Reporte.objects.filter(cliente__asesor_coordinador=self, cliente__seguimiento='cerrado_exitoso').count()

class Coordinador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    es_asesor = models.BooleanField(default=False)
    asesores = models.ManyToManyField('Asesor', related_name='coordinador_asesores')
    
    def __str__(self):
        return f'Coordinador: {self.usuario.username}'
