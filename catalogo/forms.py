from django import forms

from .models import Vuelo


class VueloForm(forms.ModelForm):
    class Meta:
        model = Vuelo
        fields = [
            "aerolinea", "codigo_vuelo", "origen", "destino", "fecha_salida",
            "descripcion", "tarifa", "cupos_disponibles", "estado", "imagen", "activo",
        ]
        widgets = {
            "aerolinea": forms.Select(attrs={"class": "form-select"}),
            "codigo_vuelo": forms.TextInput(attrs={"class": "form-control", "placeholder": "LA800"}),
            "origen": forms.TextInput(attrs={"class": "form-control"}),
            "destino": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_salida": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "tarifa": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "cupos_disponibles": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_salida"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"]
        self.fields["aerolinea"].queryset = self.fields["aerolinea"].queryset.filter(activa=True)

    def clean_codigo_vuelo(self):
        codigo = self.cleaned_data["codigo_vuelo"].strip().upper()
        existe = Vuelo.objects.filter(codigo_vuelo__iexact=codigo)
        if self.instance.pk:
            existe = existe.exclude(pk=self.instance.pk)
        if existe.exists():
            raise forms.ValidationError("Ya existe un vuelo con ese código.")
        return codigo

    def clean_tarifa(self):
        tarifa = self.cleaned_data["tarifa"]
        if tarifa is None or tarifa <= 0:
            raise forms.ValidationError("La tarifa debe ser mayor a 0.")
        return tarifa

    def clean_cupos_disponibles(self):
        cupos = self.cleaned_data["cupos_disponibles"]
        if cupos is None or cupos < 0:
            raise forms.ValidationError("Los cupos no pueden ser negativos.")
        return cupos
