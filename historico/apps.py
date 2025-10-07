from django.apps import AppConfig


class HistoricoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "historico"

    def ready(self):
        """Importa os signals e admin hooks quando o app está pronto"""
        import historico.signals  # noqa
        import historico.admin_hooks  # noqa
