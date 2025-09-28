from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json

from .models import MensagemAniversario, TemplateMensagem, TipoMensagem, StatusMensagem
from .services import MensagemService


@login_required
def enviar_mensagens_view(request):
    """View para exibir a interface de envio de mensagens"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            destinatarios = data.get('destinatarios', [])
            tipo_mensagem = data.get('tipo_mensagem')
            conteudo = data.get('conteudo')
            template_id = data.get('template_id')
            
            if not destinatarios or not tipo_mensagem or not conteudo:
                return JsonResponse({'success': False, 'error': 'Dados incompletos'}, status=400)
            
            # Processar envio das mensagens
            service = MensagemService()
            resultados = []
            
            for destinatario in destinatarios:
                try:
                    resultado = service.enviar_mensagem(
                        destinatario_nome=destinatario['nome'],
                        destinatario_telefone=destinatario['telefone'],
                        destinatario_tipo=destinatario['tipo'],
                        destinatario_id=destinatario['id'],
                        tipo_mensagem=tipo_mensagem,
                        conteudo=conteudo,
                        template_usado=template_id,
                        enviado_por=request.user
                    )
                    resultados.append(resultado)
                except Exception as e:
                    resultados.append({
                        'success': False,
                        'error': str(e),
                        'destinatario': destinatario['nome']
                    })
            
            return JsonResponse({
                'success': True,
                'resultados': resultados,
                'total_enviadas': len([r for r in resultados if r.get('success')])
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    # GET - exibir formulário
    templates = TemplateMensagem.objects.filter(ativo=True).order_by('nome')
    context = {
        'templates': templates,
        'tipos_mensagem': TipoMensagem.choices
    }
    return render(request, 'mensagens/enviar_mensagens.html', context)


@login_required
def get_templates_view(request):
    """API para buscar templates por tipo de mensagem"""
    tipo = request.GET.get('tipo')
    if not tipo:
        return JsonResponse({'error': 'Tipo de mensagem não especificado'}, status=400)
    
    templates = TemplateMensagem.objects.filter(
        tipo_mensagem=tipo,
        ativo=True
    ).values('id', 'nome', 'conteudo')
    
    return JsonResponse({'templates': list(templates)})


@login_required
def historico_mensagens_view(request):
    """View para exibir histórico de mensagens enviadas"""
    mensagens = MensagemAniversario.objects.select_related('enviado_por').order_by('-data_envio')
    
    # Filtros
    tipo_filtro = request.GET.get('tipo')
    status_filtro = request.GET.get('status')
    
    if tipo_filtro:
        mensagens = mensagens.filter(tipo_mensagem=tipo_filtro)
    if status_filtro:
        mensagens = mensagens.filter(status=status_filtro)
    
    context = {
        'mensagens': mensagens,
        'tipos_mensagem': TipoMensagem.choices,
        'status_mensagem': StatusMensagem.choices,
        'tipo_filtro': tipo_filtro,
        'status_filtro': status_filtro
    }
    return render(request, 'mensagens/historico_mensagens.html', context)


@login_required
def gerenciar_templates_view(request):
    """View para gerenciar templates de mensagem"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        tipo_mensagem = request.POST.get('tipo_mensagem')
        conteudo = request.POST.get('conteudo')
        
        if nome and tipo_mensagem and conteudo:
            TemplateMensagem.objects.create(
                nome=nome,
                tipo_mensagem=tipo_mensagem,
                conteudo=conteudo,
                criado_por=request.user
            )
            messages.success(request, 'Template criado com sucesso!')
        else:
            messages.error(request, 'Todos os campos são obrigatórios!')
        
        return redirect('gerenciar_templates')
    
    templates = TemplateMensagem.objects.filter(ativo=True).order_by('nome')
    context = {
        'templates': templates,
        'tipos_mensagem': TipoMensagem.choices
    }
    return render(request, 'mensagens/gerenciar_templates.html', context)
