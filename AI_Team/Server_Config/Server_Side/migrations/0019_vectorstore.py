# Generated by Django 4.2.5 on 2024-05-17 16:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("Server_Side", "0018_client_is_active_client_is_staff"),
    ]

    operations = [
        migrations.CreateModel(
            name="VectorStore",
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
                ("collection_name", models.CharField(max_length=255)),
                ("documents", models.JSONField()),
                ("embeddings", models.JSONField()),
                ("is_temporary", models.BooleanField(default=False)),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "client",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
