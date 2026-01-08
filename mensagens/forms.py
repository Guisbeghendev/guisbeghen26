from django import forms
from .models import SalaChat

class ExportarMensagensForm(forms.Form):
    sala = forms.ModelChoiceField(
        queryset=SalaChat.objects.all(),
        required=True,
        label="Selecionar Sala"
    )
    data_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label="Data Inicial"
    )
    data_fim = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label="Data Final"
    )