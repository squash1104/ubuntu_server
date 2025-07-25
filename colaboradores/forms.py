from django import forms
from .models import Colaborador
from geografia.models import Bairro

class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ['nome', 'telefone', 'cidade', 'bairro']
        labels = {
            'nome': 'Nome:',
            'telefone': 'Telefone:',
            'cidade': 'Cidade:',
            'bairro': 'Bairro:',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefone'].widget.attrs.update({'class': 'form-control'})

        self.fields['cidade'].empty_label = "Selecione uma cidade"
        self.fields['bairro'].empty_label = "Primeiro escolha uma cidade"

        self.fields['cidade'].widget.attrs.update({'class': 'select2'})
        self.fields['bairro'].widget.attrs.update({'class': 'select2'})

        self.fields['bairro'].queryset = Bairro.objects.none()

        # Lógica para carregar os bairros se o formulário já tiver dados (ex: na edição)
        if 'cidade' in self.data:
            try:
                cidade_id = int(self.data.get('cidade'))
                self.fields['bairro'].queryset = Bairro.objects.filter(cidade_id=cidade_id).order_by('nome_bairro')
            except (ValueError, TypeError):
                pass  # Ignora erros se o valor não for um número
        elif self.instance.pk and self.instance.cidade:
            self.fields['bairro'].queryset = self.instance.cidade.bairro_set.order_by('nome_bairro')
