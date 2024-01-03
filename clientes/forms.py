from django import forms
from .models import Cliente, Reporte
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError


class ClienteForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)
        self.user = user

        # Aplicar clases de Bootstrap a todos los widgets
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Cliente
        fields = ['nombre_completo', 'dni', 'celular', 'descripcion', 'origen_del_prospecto', 'seguimiento', 'motivo_de_compra', 'lugar_de_origen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def save(self, commit=True):
        cliente = super().save(commit=False)
        cliente.asesor_coordinador = self.user  # Asigna el usuario como asesor o coordinador.

        if commit:
            cliente.save()
        return cliente

# Reportes
class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ['descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        }

    

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        # Tu lógica de validación personalizada aquí
        if not user.is_active:
            raise ValidationError("Tu cuenta está desactivada. Comunícate con el soporte técnico.")

        # Puedes agregar más validaciones según sea necesario
        # Por ejemplo, podrías verificar si el usuario pertenece a un grupo específico

        # Llama al método original para realizar la confirmación estándar
        return super().confirm_login_allowed(user)

    


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class DateSelectForm(forms.Form):
    fecha = forms.DateField(widget=forms.SelectDateWidget(), label='Seleccionar Fecha')

    def __init__(self, *args, **kwargs):
        super(DateSelectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('submit', 'Ver eventos'))