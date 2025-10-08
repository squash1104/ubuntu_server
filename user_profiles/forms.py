from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import Profile


class ProfileForm(forms.ModelForm):
    """Formulário para edição do perfil do usuário"""
    first_name = forms.CharField(
        max_length=150,
        label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    last_name = forms.CharField(
        max_length=150,
        label='Sobrenome',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=False
    )

    remove_photo = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput(),
        initial=False
    )

    class Meta:
        model = Profile
        fields = ['photo']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Inicializar campos do User com dados atuais
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        if self.user and commit:
            # Atualizar campos do User
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.save()
            
            # Remover foto se solicitado
            if self.cleaned_data.get('remove_photo'):
                if profile.photo:
                    profile.photo.delete(save=False)
                profile.photo = None
            
            # Salvar perfil
            profile.user = self.user
            profile.save()
        
        return profile


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulário personalizado para troca de senha"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar classes Bootstrap aos campos
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
        
        # Adicionar placeholders
        self.fields['old_password'].widget.attrs.update({'placeholder': 'Digite sua senha atual'})
        self.fields['new_password1'].widget.attrs.update({'placeholder': 'Digite sua nova senha'})
        self.fields['new_password2'].widget.attrs.update({'placeholder': 'Confirme sua nova senha'})
