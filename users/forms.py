from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Profile

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'bg-white border border-silver/40 rounded px-4 py-3 text-black focus:outline-none focus:border-primary-purple transition-all duration-200'

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'nome',
            'sobrenome',
            'foto',
            'biografia',
            'contato',
            'whatsapp',
            'cidade',
            'estado',
            'data_nascimento',
            'origem_contato'
        ]
        labels = {
            'origem_contato': 'Como você conhece o GuiSbeghen?'
        }
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'biografia': forms.Textarea(attrs={'rows': 3}),
            'origem_contato': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'bg-white border border-silver/40 rounded px-4 py-3 text-black focus:outline-none focus:border-primary-purple transition-all duration-200'