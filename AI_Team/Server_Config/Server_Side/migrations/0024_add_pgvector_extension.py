# Generated by Django 4.2.5 on 2024-05-17 22:16

from django.db import migrations
from pgvector.django import VectorExtension

class Migration(migrations.Migration):
    dependencies = [
        ("Server_Side", "0023_remove_userragdata_documents"),
    ]

    operations = [VectorExtension(),]
