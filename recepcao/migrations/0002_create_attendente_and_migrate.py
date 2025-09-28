from django.db import migrations, models
import django.db.models.deletion


def forwards_populate_attendentes(apps, schema_editor):
    Attendente = apps.get_model("recepcao", "Attendente")
    Atendimento = apps.get_model("recepcao", "Atendimento")
    try:
        User = apps.get_model("auth", "User")
    except LookupError:
        User = None

    # find distinct user ids referenced in Atendimento.atendente (old data)
    qs = Atendimento.objects.values_list("atendente", flat=True).distinct()
    ids = [i for i in qs if i]
    for uid in ids:
        if Attendente.objects.filter(pk=uid).exists():
            continue
        nome = str(uid)
        if User:
            try:
                u = User.objects.get(pk=uid)
                nome = u.get_full_name() or u.username
            except Exception:
                pass
        # create Attendente with same PK to preserve existing FK integers
        Attendente.objects.create(id=uid, nome=nome)


def noop_reverse(apps, schema_editor):
    # no reverse data migration
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("recepcao", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attendente",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome", models.CharField(max_length=150)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["nome"]},
        ),
        migrations.RunPython(forwards_populate_attendentes, noop_reverse),
        migrations.AlterField(
            model_name="atendimento",
            name="atendente",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="atendimentos_assumidos",
                to="recepcao.attendente",
            ),
        ),
    ]
