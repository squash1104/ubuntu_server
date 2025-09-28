from django.db import migrations


def populate_attendentes(apps, schema_editor):
    Attendente = apps.get_model('recepcao', 'Attendente')
    Atendimento = apps.get_model('recepcao', 'Atendimento')
    # migrate existing user reference values in atendimento.atendente (integers)
    # If Attendente with that PK exists (created in previous migration), leave it.
    for a in Atendimento.objects.all():
        if a.atendente_id and not Attendente.objects.filter(pk=a.atendente_id).exists():
            # create a placeholder
            Attendente.objects.create(id=a.atendente_id, nome=f"Atendente {a.atendente_id}")


class Migration(migrations.Migration):
    dependencies = [
        ('recepcao', '0002_create_attendente_and_migrate'),
    ]

    operations = [
        migrations.RunPython(populate_attendentes, lambda apps, schema_editor: None),
    ]


