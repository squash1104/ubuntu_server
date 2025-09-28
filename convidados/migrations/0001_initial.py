from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("geografia", "__first__"),
        ("colaboradores", "__first__"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="Convidado",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("nome", models.CharField(max_length=100)),
                        ("telefone", models.CharField(max_length=20, blank=True, null=True)),
                        ("data_cadastro", models.DateTimeField(auto_now_add=True)),
                        ("cidade", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="geografia.cidade")),
                        ("bairro", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="geografia.bairro")),
                        ("colaborador", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="convidados", to="colaboradores.colaborador")),
                    ],
                    options={
                        "db_table": "convidados",
                        "verbose_name": "Convidado",
                        "verbose_name_plural": "Convidados",
                        "ordering": ["nome"],
                    },
                )
            ],
        )
    ]


