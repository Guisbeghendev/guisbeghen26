from django import forms
from .models import Galeria, MarcaDagua, ConfiguracaoHome

class GaleriaForm(forms.ModelForm):
    data_evento = forms.DateField(
        label="Data do Evento",
        required=True,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date'}
        )
    )

    class Meta:
        model = Galeria
        fields = [
            'titulo',
            'categoria',
            'data_evento',
            'acesso_publico',
            'grupos_audiencia',
            'marca_dagua_padrao',
            'status'
        ]
        widgets = {
            'grupos_audiencia': forms.CheckboxSelectMultiple(),
            'titulo': forms.TextInput(attrs={'placeholder': 'Ex: Casamento Maria e João'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['titulo'].required = True
        self.fields['categoria'].required = True
        self.fields['grupos_audiencia'].required = True
        self.fields['marca_dagua_padrao'].required = False
        self.fields['acesso_publico'].required = False

        self.fields['data_evento'].localize = False
        self.fields['data_evento'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']

        if user:
            self.fields['marca_dagua_padrao'].queryset = MarcaDagua.objects.filter(fotografo=user)

class MarcaDaguaForm(forms.ModelForm):
    class Meta:
        model = MarcaDagua
        fields = ['nome', 'imagem', 'opacidade']
        widgets = {
            'opacidade': forms.NumberInput(attrs={'min': '0', 'max': '100'}),
        }

class ConfiguracaoHomeForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoHome
        fields = ['hero_imagem', 'hero_arte_sobreposta', 'hero_legenda']
        labels = {
            'hero_imagem': 'Imagem de Fundo (Hero)',
            'hero_arte_sobreposta': 'Arte Sobreposta (PNG Transparente)',
            'hero_legenda': 'Legenda Opcional'
        }
        widgets = {
            'hero_legenda': forms.TextInput(attrs={'placeholder': 'Ex: Momentos Inesquecíveis'}),
        }