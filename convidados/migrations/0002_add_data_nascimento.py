from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("convidados", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="convidado",
            name="data_nascimento",
            field=models.DateField(null=True, blank=True),
        ),
    ]


