# Generated by Django 4.2.5 on 2023-10-03 21:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "Server_Side",
            "0011_alter_client_current_plan_alter_client_method_pay_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="last_transaction_status",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="client",
            name="order_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
