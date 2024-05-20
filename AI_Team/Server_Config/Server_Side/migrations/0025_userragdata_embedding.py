# Generated by Django 4.2.5 on 2024-05-17 22:56

from django.db import migrations
import pgvector.django


class Migration(migrations.Migration):
    dependencies = [
        ("Server_Side", "0024_add_pgvector_extension"),
    ]

    operations = [
        migrations.AddField(
            model_name="userragdata",
            name="embedding",
            field=pgvector.django.VectorField(dimensions=4096, null=True),
        ),
    ]
