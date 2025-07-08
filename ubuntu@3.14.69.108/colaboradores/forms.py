from django import forms
from .models import Colaborador

class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ['nome', 'contato', 'cidade', 'bairro', 'cargo']
        # Opcional: Adicionar labels personalizados para os campos
        labels = {
            'nome': 'Nome Completo',
            'contato': 'Contato (Telefone/Email)',
            'cidade': 'Cidade',
            'bairro': 'Bairro',
            'cargo': 'Cargo/Função',
        }
