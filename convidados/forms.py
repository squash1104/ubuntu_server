from django import forms
from .models import Convidado
from colaboradores.models import Colaborador # Importa o modelo Colaborador

class ConvidadoForm(forms.ModelForm):
    class Meta:
        model = Convidado
        fields = ['nome', 'telefone', 'email', 'cidade', 'bairro', 'colaborador']
        labels = {
            'nome': 'Nome Completo do Convidado',
            'telefone': 'Telefone do Convidado',
            'email': 'Email do Convidado',
            'cidade': 'Cidade do Convidado',
            'bairro': 'Bairro do Convidado',
            'colaborador': 'Convidado por',
        }
