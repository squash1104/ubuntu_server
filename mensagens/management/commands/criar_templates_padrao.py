from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mensagens.models import TemplateMensagem


class Command(BaseCommand):
    help = 'Cria templates padrão para mensagens de aniversário'

    def handle(self, *args, **options):
        # Buscar o primeiro usuário admin ou criar um padrão
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
        except:
            user = None

        templates = [
            {
                'nome': 'SMS Simples',
                'tipo_mensagem': 'sms',
                'conteudo': 'Parabéns {nome}! Hoje é seu aniversário. Desejamos muitas felicidades! Atenciosamente, Equipe Sistema Fidelização'
            },
            {
                'nome': 'SMS Completo',
                'tipo_mensagem': 'sms',
                'conteudo': '🎉 Parabéns {nome}! 🎉\n\nHoje é seu aniversário e queremos te desejar muitas felicidades!\n\nQue este novo ano de vida seja repleto de alegrias e conquistas!\n\nAtenciosamente,\nEquipe Sistema Fidelização'
            },
            {
                'nome': 'WhatsApp Simples',
                'tipo_mensagem': 'whatsapp',
                'conteudo': '🎉 *Parabéns {nome}!* 🎉\n\nHoje é seu aniversário! Desejamos muitas felicidades!\n\nAtenciosamente,\n*Equipe Sistema Fidelização*'
            },
            {
                'nome': 'WhatsApp Completo',
                'tipo_mensagem': 'whatsapp',
                'conteudo': '🎉 *Parabéns {nome}!* 🎉\n\nHoje é um dia muito especial! Queremos te desejar um feliz aniversário e muitas felicidades!\n\nQue este novo ano de vida seja repleto de:\n✨ Alegrias\n✨ Conquistas\n✨ Momentos especiais\n✨ Muito sucesso!\n\n🎂 *Feliz Aniversário!* 🎂\n\nAtenciosamente,\n*Equipe Sistema Fidelização*'
            }
        ]

        created_count = 0
        for template_data in templates:
            template, created = TemplateMensagem.objects.get_or_create(
                nome=template_data['nome'],
                defaults={
                    'tipo_mensagem': template_data['tipo_mensagem'],
                    'conteudo': template_data['conteudo'],
                    'criado_por': user,
                    'ativo': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Template criado: {template.nome}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Template já existe: {template.nome}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Processo concluído! {created_count} templates criados.')
        )
